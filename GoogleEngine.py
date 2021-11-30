import pandas as pd
from scholarly import scholarly
from Scraper import ScraperAPI


class GoogleEngine:
    def __init__(self, scraper_key):
        self.pg = ScraperAPI(scraper_key)
        scholarly.use_proxy(self.pg)
        scholarly.set_timeout(120)
        self.search_list = None
        self.df = None

    def __get_papers(self, search_string, year_interval, patents, citations):
        search_query = scholarly.search_pubs(
            query=search_string,
            patents=patents,
            citations=citations,
            year_low=year_interval[0],
            year_high=year_interval[1]
        )
        self.search_list = list(search_query)

    def __dict_to_df(self):
        cols = ['title', 'author', 'year', 'venue', 'abstract', 'container_type', 'gsrank', 'num_citations']
        main_list = []

        for d in self.search_list:
            row = []
            for key in d:
                if key == 'bib':
                    row.append(d[key]['title'])
                    row.append(d[key]['author'])
                    row.append(d[key]['pub_year'])
                    row.append(d[key]['venue'])
                    if 'abstract' in d[key]:
                        row.append(d[key]['abstract'])
                    else:
                        row.append('no abstract')
            row.append(d['container_type'])
            row.append(d['gsrank'])
            row.append(d['num_citations'])

            main_list.append(row)
        self.df = pd.DataFrame(main_list, columns=cols)

    @staticmethod
    def get_citation(df):
        citation_dict = {}
        len_df = len(df)

        for index, row in df.iterrows():
            title = row[1]
            year_low = row[0] - 1
            year_high = row[0] + 1
            search_query = scholarly.search_pubs(query=title, year_low=year_low, year_high=year_high)
            try:
                query_result = next(search_query)
                citation_dict[index] = query_result['num_citations']
                print(str(index) + '/' + str(len_df), str(query_result['num_citations']) + ' - ' + title)
            except:
                citation_dict[index] = -1
                print(str(index) + '/' + str(len_df), str(-1) + ' - ' + title)
                # print(query_result)

        df['citation'] = citation_dict.values()
        # df.to_csv('venue_files/citation/citation.csv')
        return df

    def search(self, search_string, year_interval, patents=False, citations=True):
        self.__get_papers(search_string, year_interval, patents, citations)
        self.__dict_to_df()
