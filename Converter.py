import re
import bibtexparser
import pandas as pd
import glob
from GoogleEngine import GoogleEngine


class Converter:
    def __init__(self):
        self.googleEngine = GoogleEngine('b1b530dd6a1154ab7c8b0e602d28c947')

    @staticmethod
    def __open_bib(bib_folder):
        with open(bib_folder, encoding='ISO-8859-1') as bibtext_files:
            bib_database = bibtexparser.load(bibtext_files)
        return bib_database

    @staticmethod
    def __merge_cols(df):
        cols = ['year', 'title', 'abstract', 'keywords', 'booktitle', 'journal', 'author']
        df_aux = df[cols].copy(deep=True)
        papers_list = []
        for index, row in df_aux.iterrows():
            if isinstance(row[4], float):
                papers_list.append(row[5])
            else:
                papers_list.append(row[4])
        df_aux['venue'] = papers_list
        return df_aux.drop(['booktitle', 'journal'], axis=1)

    # parser
    @staticmethod
    def __remove_keys(df):  # remove "{" and "}"
        return df.applymap(lambda x: x.replace('{', '').replace('}', '') if isinstance(x, str) else x)

    def bibtext_to_df(self, bib_folder):
        bib_database = self.__open_bib(bib_folder)
        df = pd.DataFrame(bib_database.entries)
        df = self.__merge_cols(df)
        if 'wos' in bib_folder:
            df = self.__remove_keys(df)
            df['engine'] = 'wos'
        elif 'sd' in bib_folder:
            df['engine'] = 'sd'
        elif 'acm' in bib_folder:
            df['engine'] = 'acm'
        df['citation'] = 0
        return df

    @staticmethod
    def csv_to_df(csv_folder):
        col = ['year', 'title', 'abstract', 'keywords', 'author', 'venue', 'engine', 'citation']
        files = glob.glob(csv_folder + '*.csv')
        df = pd.DataFrame()
        for f in files:
            csv = pd.read_csv(f)
            df = df.append(csv)

        if 'ieee' in files[0]:
            col_ieee = ['Publication Year', 'Document Title', 'Abstract', 'Author Keywords', 'Authors',
                        'Publication Title', 'engine', 'citation']
            df['engine'] = 'ieee'
            df['citation'] = 0
            df = df[col_ieee]
        elif 'scopus' in files[0]:
            col_scopus = ['Year', 'Title', 'Abstract', 'Author Keywords', 'Authors', 'Source title', 'engine',
                          'citation']
            df['engine'] = 'scopus'
            df['citation'] = 0
            df = df[col_scopus]
        else:
            col_google = ['year', 'title', 'abstract', 'keywords', 'author', 'venue', 'engine', 'num_citations']
            df['keywords'] = '-'
            df['engine'] = 'google'
            df = df[col_google]

        df.columns = col
        return df

    @staticmethod
    def __concat_engines_df(df_list):
        return pd.concat(df_list, axis=0).reset_index(drop=True)

    @staticmethod
    def __df_lower(df):
        return df.applymap(lambda x: x.lower() if type(x) == str else x)

    @staticmethod
    def __set_df(df):
        df['year'] = df['year'].fillna(0)
        df['year'] = df['year'].astype(int)

        # cleaning df. Remove thinks that does not are papers

        df = df.drop(index=df[df['title'].astype(str).str.contains('chapter')].index)
        df = df.loc[df['author'] != '']
        df = df.loc[df['author'].notna()]

        df = df.drop(index=df.loc[df['author'].str.contains('no author name available')].index)
        df = df.loc[df['venue'].notna()]
        df = df.loc[df['abstract'].notna()]

        trash_list = 'guest editor|special issue|editor-in-chief|international workshop on|international conference ' \
                     'on|world conference on|ieee access|acm|editorial|in this issue|dr. wenjing lou'
        df = df.drop(index=df.loc[df['title'].str.contains(trash_list)].index)
        df['keywords'] = df['keywords'].fillna('-')

        df.loc[df['year'] == 2022, 'year'] = 2021

        # drop papers duplicates
        df.drop_duplicates(subset=['year', 'title'], inplace=True)
        return df  # .reset_index(drop=True)

    @staticmethod
    def __remove_venues_marks(df):
        rows = []
        for index, row in df.iterrows():
            venue = row[5]
            venue = re.sub('\d{1,2}[a-zA-Z]{2}\s', '', venue)  # (e.g 2nd, 17th)
            venue = re.sub('\(\d{1,2}[a-zA-Z]{2}\)', '', venue)  # (12CT)
            venue = re.sub('\d{4}\s', '', venue)  # 2020space
            venue = re.sub('\s\d{4}', '', venue)  # space2020
            venue = re.sub('-\d{4}', '', venue)  # -2020
            venue = re.sub('\d{4}', '', venue)  # 2020
            venue = re.sub("'\d{2}", '', venue)  # '16
            venue = re.sub('\(\d*\)', '', venue)  # (48184)
            rows.append([
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                venue,
                row[6],
                row[7]
            ])
        return pd.DataFrame(rows, columns=df.columns)

    @staticmethod
    def __load_h5_index(df):
        df_char = pd.read_csv('venue_files/h5-index/citation_char.csv')
        df_number = pd.read_csv('venue_files/h5-index/citation_number.csv')

        for index, row in df_char.iterrows():
            df_number.loc[df_number['venue'] == row['venue'], 'h5-index'] = row['h5-index']

        for index, row in df_number.iterrows():
            df.loc[df['venue'] == row['venue'], 'h5-index'] = row['h5-index']

        df.loc[df['venue'].str.contains('arxiv'), 'h5-index'] = 22
        added = df['h5-index'].notnull().sum()
        total = len(df)
        missing = df['h5-index'].isnull().sum()

        print('Were added ' + str(added) + '/' + str(total) + ' are missing ' + str(missing) + ' - ' + str(
            missing / total * 100)[:5] + '%')

        df['h5-index'] = df['h5-index'].fillna(0)
        return df

    @staticmethod
    def __load_quartile(df):
        df_scimago = pd.read_csv('venue_files/scimago/scimago.csv')
        for y in range(2011, 2022):
            for index, row in df_scimago.iterrows():
                if y < 2021:
                    df.loc[(df['venue'] == row['Title']) &
                           (df['year'] == y), 'qtl'] = row[str(y) + '_qtl']
                else:
                    df.loc[(df['venue'] == row['Title']) &
                           (df['year'] == y), 'qtl'] = row[str(y - 1) + '_qtl']
        df['qtl'] = df['qtl'].fillna('-')
        return df

    def __load_citation(self, df):
        df = self.googleEngine.get_citation(df)
        return df

    def prepare_df(self, df_list):
        print('Concatenating the engines...')
        df = self.__concat_engines_df(df_list)
        print('Converting whole data frame to lower case...')
        df = self.__df_lower(df)
        print('Cleaning the data frame...')
        df = self.__set_df(df)
        print('Removing venues marks...')
        df = self.__remove_venues_marks(df)
        print('Adding h5-index...')
        df = self.__load_h5_index(df)
        print('Adding Scimago quartile...')
        df = self.__load_quartile(df)
        # df = pd.read_csv('venue_files/df.csv')
        print('Adding citation number...')
        df = self.__load_citation(df)

        return df
