# Projeto final de Programacao
# Autor: Lauro Henriko Garcia Alves de Souza.
# Matricula: 1912713
# Orientador: Waldemar Celes

# ==============================================================================

"""Converte valores em pixels em coordenadas do mundo real.


1. Dada a matriz da camera.
2. Transforma pixels em lat-long

Este e o arquivo auxilia o dash.py nas estaticas de localizacao.
"""

# ==============================================================================



import numpy as np


def project_points_to3d_multi_points(points_2d):
    M = np.array([[  2.86963955e-02,  -1.07200344e-02,   9.92993629e-01],
       [ -1.78631638e-03,   8.30670204e-03,   1.13811483e-01],
       [ -4.99762745e-06,   6.45838231e-06,  -6.73876953e-05]])
    # concatenate w aos px,py
    points_2d = np.concatenate((points_2d, np.ones((9, 1))), axis=1)
    # print points_2d
    # calcula a inversa de M
    inversa_M = np.linalg.inv(M)
    # print inversa_M
    # produto interno de inv(M) e pontos 2d com w
    points_3d_projected_plan = np.dot(inversa_M, points_2d.T).T
    # print points_3d_projected_plan

    # X,Y dividindo pelo w de X,Y
    X, Y = points_3d_projected_plan[:, 0] / points_3d_projected_plan[:, 2], points_3d_projected_plan[:,
                                                                            1] / points_3d_projected_plan[:, 2]

    points_3d_plano = np.hstack((X[:, np.newaxis], Y[:, np.newaxis]))

    return points_3d_plano



def project_points_to3d(points_2d):
    M = np.array([[  2.88129591e-02,  -1.08270262e-02,   9.95568408e-01],
       [ -2.04361445e-03,   7.68923249e-03,   8.85030986e-02],
       [ -1.20775854e-05,   1.45513834e-05,  -1.87137935e-04]])
    # concatenate w aos px,py
    w = np.ones(1)
    points_2d = np.concatenate((points_2d, w), axis=0)
    # print points_2d
    # calcula a inversa de M
    inversa_M = np.linalg.inv(M)
    # print inversa_M
    # produto interno de inv(M) e pontos 2d com w
    points_3d_projected_plan = np.dot(inversa_M, points_2d.T).T
    # print points_3d_projected_plan

    # X,Y dividindo pelo w de X,Y
    X, Y = points_3d_projected_plan[0] / points_3d_projected_plan[2], points_3d_projected_plan[1] / points_3d_projected_plan[2]

    points_3d_plano = np.hstack((X, Y))

    return points_3d_plano



#matriz da camera


p_m_sem_z = np.array([[  2.86963955e-02,  -1.07200344e-02,   9.92993629e-01],
       [ -1.78631638e-03,   8.30670204e-03,   1.13811483e-01],
       [ -4.99762745e-06,   6.45838231e-06,  -6.73876953e-05]])


