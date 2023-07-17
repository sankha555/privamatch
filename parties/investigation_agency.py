import numpy as np
from Pyfhel import Pyfhel
import rsa

PROFILE_SLOTS = 10
FIELD_SIZE = 65537
DATABASE_SIZE = 10

class InvestigationAgency():
  def __init__(self, crime_sample, suspect_ids, model = "Ideal"):
    self.suspect_ids = suspect_ids
    self.d_s = crime_sample
    self.d_s_HE = []
    self.num_suspects = len(suspect_ids)
    self.psi_suspects = []
    self.public_keys = []
    self.private_keys = []
    self.dna_matches = []
    self.pi_1_inv = []
    self.pi_2_inv = []
    self.zero_HE = 0
    self.one_HE = 0
    self.Delta_HE = []

  def decrypt_DNA_profile(self, y, key):
    m, n = len(y), len(y[0])
    assert n == 2
    for i in range(m):
      y[i][0] = rsa.decrypt(y[i][0], key).decode()
      y[i][1] = rsa.decrypt(y[i][1], key).decode()

    print(y)
    y_prime = np.array(y)
    print(y_prime)
    return y_prime

  def generate_OT_keys(self):
    self.public_keys = []
    self.private_keys = []

    import rsa
    for i in range(DATABASE_SIZE):
      pk, sk = rsa.newkeys(2048)
      self.public_keys.append(pk)
      if i < self.num_suspects:
        self.private_keys.append(sk)

  def pi(self, K):
    from random import randint
    K_pi = [None] * DATABASE_SIZE

    for j, i in enumerate(self.suspect_ids):
      K_pi[i] = K[j]

    i = 0
    from numpy import random
    leftover_indices = list(range(self.num_suspects, DATABASE_SIZE))
    random.shuffle(leftover_indices)
    for j in range(len(K_pi)):
      if K_pi[j] is None:
        K_pi[j] = K[leftover_indices[i]]
        i += 1

    return K_pi

  def receiver_OT_actions(self, Y):
    for i in range(self.num_suspects):
      # sk = self.private_keys[i]
      s_i = self.suspect_ids[i]

      # y_s_i = self.decrypt_DNA_profile(Y[s_i], sk)
      y_s_i = Y[s_i]
      self.psi_suspects.append(y_s_i)

  def pi_1(self, Omega):
    from numpy import random

    w = len(Omega)
    indices = [i for i in range(w)]
    random.shuffle(indices)

    self.pi_1_inv = indices

    Omega_pi = [Omega[i] for i in indices]

    return Omega_pi

  def pi_2(self, Gamma):
    from numpy import random

    g = len(Gamma)
    indices = [i for i in range(g)]
    random.shuffle(indices)

    self.pi_2_inv = indices

    Gamma_pi = [Gamma[i] for i in indices]

    return Gamma_pi

  def inv_pi_1(self, Omega_pi):
    Omega = [None]*len(self.pi_1_inv)
    for i, ind in enumerate(self.pi_1_inv):
      Omega[ind] = Omega_pi[i]
    return Omega

  def inv_pi_2(self, Gamma_pi):
    Gamma = [None]*len(self.pi_2_inv)
    for i, ind in enumerate(self.pi_2_inv):
      Gamma[ind] = Gamma_pi[i]
    return Gamma

  def get_masks(self, i, j):
    x = self.d_s[i][j]

    import galois
    from random import randint
    from math import sqrt

    Z_p = galois.GF(FIELD_SIZE)

    w = 30
    Omega = Z_p([randint(2, (FIELD_SIZE)) for i in range(w)])

    g = randint(w//2, w-1)
    Gamma = []
    for i in range(w):
      r = Omega[i]
      if i < g:
        r_prime = r**-1
        Gamma.append(r_prime)
      else:
        r_prime = randint(2, (FIELD_SIZE))
        Gamma.append(r_prime)

    Omega_pi = [(x * r) % FIELD_SIZE for r in self.pi_1(Omega)]
    Gamma_pi = self.pi_2(Gamma)

    return Omega_pi, Gamma_pi, g

  def compute_element_HE_encryption(self, Y_Omega, Y_Gamma, g):
    from random import randint

    Y_Omega = self.inv_pi_1(Y_Omega)
    Y_Gamma = self.inv_pi_2(Y_Gamma)

    t = randint(0, g-1)
    x_HE = Y_Omega[t] * Y_Gamma[t]

    return x_HE

  def find_similarities(self):
    Delta_HE = []

    d_s_HE = self.d_s_HE

    for j, d_i_HE in enumerate(self.psi_suspects):
      zero_HE = self.zero_HE
      zero_HE = zero_HE*zero_HE
      zero_HE = zero_HE*zero_HE # size 5/5

      delta_HE_1 = zero_HE
      delta_HE_2 = zero_HE

      for i in range(PROFILE_SLOTS):
        delta_1 = (d_i_HE[i][0]*self.one_HE - d_s_HE[i][0])*(d_i_HE[i][0]*self.one_HE - d_s_HE[i][0])
        delta_2 = (d_i_HE[i][1]*self.one_HE - d_s_HE[i][1])*(d_i_HE[i][1]*self.one_HE - d_s_HE[i][1])

        delta_HE_1 = (delta_HE_1 + delta_1)
        delta_HE_2 = (delta_HE_2 + delta_2)

      Delta_HE.append((delta_HE_1, delta_HE_2))

    self.Delta_HE = Delta_HE