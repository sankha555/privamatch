import numpy as np
from Pyfhel import Pyfhel
import rsa

PROFILE_SLOTS = 10
FIELD_SIZE = 65537
DATABASE_SIZE = 10

class Judiciary():
  def __init__(self):
    self.suspect_ids = []
    self.num_suspects = 0
    self.d_s = None
    self.psi_suspects = []
    self.public_keys = []
    self.private_keys = []
    self.Delta = []

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
      sk = self.private_keys[i]
      s_i = self.suspect_ids[i]

      y_s_i = self.decrypt_DNA_profile(Y[s_i], sk)
      self.psi_suspects.append(y_s_i)

  def decrypt_DNA_profile(self, y, key):
    m, n = len(y), len(y[0])
    assert n == 2
    for i in range(m):
      y[i][0] = int(rsa.decrypt(y[i][0], key).decode("utf-8"))
      y[i][1] = int(rsa.decrypt(y[i][1], key).decode("utf-8"))
    return np.array(y)

  def find_similarities(self):
    Delta = []
    d_s = self.d_s
    assert d_s is not None
    for j, d_i in enumerate(self.psi_suspects):
      delt = 0
      s_i = self.suspect_ids[j]
      for i in range(PROFILE_SLOTS):
        delt_1 = (d_i[i][0] - d_s[i][0])*(d_i[i][0] - d_s[i][0])
        delt_2 = (d_i[i][1] - d_s[i][1])*(d_i[i][1] - d_s[i][1])
        delt += delt_1 * delt_2
      Delta.append((s_i, delt))
    self.Delta = Delta

  def find_matches(self, threshold):
    from math import sqrt
    matches = []
    for s_i, delta in self.Delta:
      if sqrt(delta) < threshold:
        matches.append(s_i)

    return matches