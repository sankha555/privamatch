import numpy as np
from Pyfhel import Pyfhel
import rsa

from parties.forensic_lab import ForensicLab
from parties.investigation_agency import InvestigationAgency


PROFILE_SLOTS = 10
FIELD_SIZE = 65537
DATABASE_SIZE = 10

class RealWorld():
  def __init__(self, I, L):
    self.I = I
    self.L = L

  def get_profiles(self):
    # At I
    self.I.generate_OT_keys()
    K = self.I.public_keys
    K_pi = self.I.pi(K)
    K_pi = []

    # At L
    Y = self.L.sender_OT_actions(K_pi)

    # At I
    self.I.receiver_OT_actions(Y)

  def get_encrypted_crime_scene_DNA_profile(self):
    for x in range(PROFILE_SLOTS):
      self.I.d_s_HE.append([None, None])
      for y in [0, 1]:
        Omega_pi_1, Gamma_pi_2, g = self.I.get_masks(x, y)

        assert len(Omega_pi_1) == len(Gamma_pi_2)
        w = len(Omega_pi_1)

        Y_Omega = []
        Y_Gamma = []
        for i in range(w):
          x_Omega = Omega_pi_1[i]
          x_Gamma = Gamma_pi_2[i]

          Y_Omega.append(self.L.encrypt_HE(x_Omega))
          Y_Gamma.append(self.L.encrypt_HE(x_Gamma))

        kappa_prime = self.I.compute_element_HE_encryption(Y_Omega, Y_Gamma, g)

        self.I.d_s_HE[x][y] = kappa_prime
      self.I.zero_HE = self.L.encrypt_HE(0)
      # print(self.L.decrypt_HE(self.I.zero_HE))
      self.I.one_HE = self.L.encrypt_HE(1)
      # print(self.L.decrypt_HE(self.I.one_HE))


  def find_DNA_similarities(self):
    self.I.find_similarities()

  def find_DNA_matches(self, threshold):
    self.I.dna_matches = [self.I.suspect_ids[i] for i in self.L.find_matches(self.I.Delta_HE, threshold)]


if __name__ == "__main__":
    crime_sample = np.array([
        [16, 34],
        [78, 109],
        [56, 532],
        [42, 324],
        [22, 983],
        [29, 499],
        [58, 193],
        [30, 202],
        [87, 324],
        [61, 224],
    ])

    I = InvestigationAgency(crime_sample=crime_sample, suspect_ids = [2, 3, 6], model="Real")

    L = ForensicLab(model="Real")

    model = RealWorld(I, L)
    model.get_profiles()

    model.get_encrypted_crime_scene_DNA_profile()
    model.find_DNA_similarities()
    matches = model.find_DNA_matches(50)

    print(model.I.dna_matches)
