import pandas as pd
import numpy as np
from pandas.api.types import CategoricalDtype
from scipy import sparse
from collections import Counter
from numpy.linalg import norm

def similarity(a, b):
    return (np.dot(a,b)+1e-7)/((norm(a)+1e-7)*(norm(b)+1e-7))


def get_recommendations_item(movie_ratings, target_user):
    users = movie_ratings.user_id.unique()
    movies = movie_ratings.movie_id.unique()
    shape = (len(users), len(movies))

    

    user_cat = CategoricalDtype(categories=sorted(users), ordered=True)
    movie_cat = CategoricalDtype(categories=sorted(movies), ordered=True)
    user_index =movie_ratings.user_id.astype(user_cat).cat.codes
    movie_index = movie_ratings.movie_id.astype(movie_cat).cat.codes

    coo = sparse.coo_matrix((movie_ratings.rating, (user_index, movie_index)), shape=shape)
    csr = coo.tocsr()

    ratings = np.asarray(csr.todense(), dtype=np.float64)


    target_user_idx = np.where(users==target_user)[0][0]
    rated_movie_idx = np.argsort(ratings[target_user_idx])[::-1][:len(ratings[target_user_idx][ratings[target_user_idx] != 0])]

    for i in range(ratings.shape[0]):
        ratings[i] -= (ratings[i]>0).astype(np.float64) * (ratings[i][ratings[i]>0]).mean()


    ans = np.zeros((ratings.shape[1],))
    for i in range(ans.shape[0]):
        similarity_sum = 0
        rating_sum = 0
        for j in rated_movie_idx:
            sim = similarity(ratings[:, i], ratings[:, j])
            rating_sum += (sim * ratings[target_user_idx, j])
            similarity_sum += sim
        ans[i] = rating_sum/(similarity_sum*ratings.shape[0])


    top_movie_idx = np.argsort(ans)[::-1]
    return list(movies[top_movie_idx])

def get_recommendations_user(movie_ratings, target_user):
    users = movie_ratings.user_id.unique()
    movies = movie_ratings.movie_id.unique()
    shape = (len(users), len(movies))

    

    user_cat = CategoricalDtype(categories=sorted(users), ordered=True)
    movie_cat = CategoricalDtype(categories=sorted(movies), ordered=True)
    user_index =movie_ratings.user_id.astype(user_cat).cat.codes
    movie_index = movie_ratings.movie_id.astype(movie_cat).cat.codes

    coo = sparse.coo_matrix((movie_ratings.rating, (user_index, movie_index)), shape=shape)
    csr = coo.tocsr()

    ratings = np.asarray(csr.todense(), dtype=np.float64)


    target_user_idx = np.where(users==target_user)[0][0]

    for i in range(ratings.shape[0]):
        ratings[i] -= (ratings[i]>0).astype(np.float64) * (ratings[i][ratings[i]>0]).mean()

    similarity_list = np.zeros((ratings.shape[0],))
    for i in range(ratings.shape[0]):
        sim = similarity(ratings[i], ratings[target_user_idx])
        similarity_list[i] = sim

    top_idx = np.argsort(similarity_list)[::-1][:]

    ans = np.zeros((ratings.shape[1],))
    similarity_sum = 0
    for i in top_idx:
        ans += ratings[i] * similarity_list[i]
        similarity_sum += similarity_list[i]

    ans /= (similarity_sum*ratings.shape[0])
    top_movie_idx = np.argsort(ans)[::-1]
    return list(movies[top_movie_idx])