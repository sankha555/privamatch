import numpy as np
from Pyfhel import Pyfhel
import rsa

PROFILE_SLOTS = 10
FIELD_SIZE = 65537
DATABASE_SIZE = 10

class ForensicLab():
  def __init__(self, model = "Ideal"):
    self.model = model

    self.C_H = None
    if model == "Real":
      self.initiate_HE()

    self.database = []  # Database of DNA profiles
    self.populate_database()

  def initiate_HE(self):
      self.C_H = Pyfhel()
      bgv_params = {
          'scheme': 'BGV',
          'n': 2**13,
          't': FIELD_SIZE,
          'sec': 128,
      }
      self.C_H.contextGen(**bgv_params)
      self.C_H.keyGen()
      self.C_H.rotateKeyGen()
      self.C_H.relinKeyGen()

  def populate_database(self):
    from random import randint
    p = FIELD_SIZE

    for i in range(DATABASE_SIZE):
      etas = [randint(10, p//100) for _ in range(PROFILE_SLOTS)] # frequencies/distances
      sigmas = [randint(10, p//100) for _ in range(PROFILE_SLOTS)]  # amplitudes

      if self.model == "Real":
        assert self.C_H is not None

        etas = [self.C_H.encryptBGV(np.array([i], dtype=np.int64)) for i in etas]
        sigmas = [self.C_H.encryptBGV(np.array([i], dtype=np.int64)) for i in sigmas]

      d_i = np.column_stack((etas, sigmas))
      self.database.append(d_i)

  def encrypt_DNA_profile(self, d, key):
    m, n = d.shape
    assert n == 2
    y = []
    for i in range(m):
      if self.model == "Ideal":
        y_0 = rsa.encrypt(str(d[i][0]).encode(), key)
        y_1 = rsa.encrypt(str(d[i][1]).encode(), key)
        y.append([y_0, y_1])
      else:
        y_0 = d[i][0]
        y_1 = d[i][1]
        y.append([y_0, y_1])
    return y

  def sender_OT_actions(self, pks):
    Y = []
    for i in range(DATABASE_SIZE):
      d_i = self.database[i]
      y_i = d_i
      if self.model == "Ideal":
        y_i = self.encrypt_DNA_profile(d_i, pks[i])
      Y.append(y_i)

    return Y

  def encrypt_HE(self, x):
    x = np.array([x], dtype=np.int64)
    return self.C_H.encryptBGV(x)

  def decrypt_HE(self, y):
    y = self.C_H.decryptBGV(y)
    return y

  def find_matches(self, Delta_HE, threshold):
    from math import sqrt
    mu = []

    for i in range(len(Delta_HE)):
      Delta_HE_eta, Delta_HE_sigma = Delta_HE[i]

      delta_1 = self.decrypt_HE(Delta_HE_eta)[0]
      if delta_1 < 0:
        delta_1 += FIELD_SIZE

      delta_2 = self.decrypt_HE(Delta_HE_sigma)[0]
      if delta_2 < 0:
        delta_2 += FIELD_SIZE

      delta = delta_1*delta_2
      if sqrt(sqrt(delta)) < threshold:
        mu.append(i)

    return mu