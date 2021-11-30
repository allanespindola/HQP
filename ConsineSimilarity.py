import pandas as pd
import gensim
from gensim.parsing.preprocessing import preprocess_documents


class CosineSimilarity:
    def __init__(self, df):
        self.df = df
        # transform keywords, title and abstract into a list
        self.text_corpus = self.df['keywords'].values + ' - ' + self.df['title'].values + ' - ' + self.df['abstract']. \
            values
        # apply the pre-processor
        self.processed_corpus = preprocess_documents(self.text_corpus)
        self.dictionary = gensim.corpora.Dictionary(self.processed_corpus)
        self.bow_corpus = [self.dictionary.doc2bow(text) for text in self.processed_corpus]
        self.tfidf = gensim.models.TfidfModel(self.bow_corpus)
        self.index = gensim.similarities.MatrixSimilarity(self.tfidf[self.bow_corpus])
        self.most_frequent_words_d = self.__get_full_bow()
        self.most_frequent_words_l = list(self.most_frequent_words_d.items())

    @staticmethod
    def __get_key(my_dict, val):
        for key, value in my_dict.items():
            if val == value:
                return key
        return "key doesn't exist"

    def __get_full_bow(self):
        my_dict = self.dictionary.token2id
        value_bow = {key: 0 for key in range(0, self.index.num_features)}

        for paper in self.bow_corpus:
            for word in paper:
                value_bow[word[0]] += word[1]
        # get dict with word's name in the key instead id/number
        name_bow = {self.__get_key(my_dict, key): value for (key, value) in value_bow.items()}
        # sort the dict by word occurrence
        name_bow = dict(sorted(name_bow.items(), key=lambda x: -x[1]))
        return name_bow

    def get_similarities(self, search_string, n_lines=10):
        new_doc = search_string
        new_doc = gensim.parsing.preprocessing.preprocess_string(new_doc)
        new_vec = self.dictionary.doc2bow(new_doc)
        vec_bow_tfidf = self.tfidf[new_vec]
        sims = self.index[vec_bow_tfidf]

        list_rank = []
        for s in sorted(enumerate(sims), key=lambda item: -item[1])[:n_lines]:
            list_rank.append(
                [self.df['title'].iloc[s[0]], self.df['year'].iloc[s[0]], self.df['mean_citation'].iloc[s[0]],
                 str(s[1])])

        return pd.DataFrame(list_rank, columns=['title' + ' - Search String: ' + search_string + ' -> ' + str(new_doc),
                                                'year', 'mean citation', 'similarity'])

    def get_similarities_mfw(self, words=10, n_lines=10):
        s_string = words
        if type(words) == int:
            s_string = ' '.join([i[0] for i in self.most_frequent_words_l[:words]])
        return self.get_similarities(search_string=s_string, n_lines=n_lines)
