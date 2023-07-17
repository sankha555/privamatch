import numpy as np
from Pyfhel import Pyfhel
import rsa

from parties.forensic_lab import ForensicLab
from parties.investigation_agency import InvestigationAgency
from parties.judiciary import Judiciary


PROFILE_SLOTS = 10
FIELD_SIZE = 65537
DATABASE_SIZE = 10

class IdealWorld():
  def __init__(self, J, I, L):
    self.J = J
    self.I = I
    self.L = L

  def communicate_suspect_ids_and_crime_sample(self):
    self.J.suspect_ids = self.I.suspect_ids
    self.J.num_suspects = self.I.num_suspects
    self.J.d_s = self.I.d_s

  def get_profiles(self):
    # At J
    self.J.generate_OT_keys()
    K = self.J.public_keys
    K_pi = self.J.pi(K)

    # At L
    Y = self.L.sender_OT_actions(K_pi)

    # At J
    self.J.receiver_OT_actions(Y)

  def find_DNA_similarities(self):
    self.J.find_similarities()

  def find_DNA_matches(self, threshold):
    self.I.dna_matches = self.J.find_matches(threshold)


if __name__ == "__main__":
    J = Judiciary()

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
    I = InvestigationAgency(crime_sample=crime_sample, suspect_ids = [2, 3, 6])

    L = ForensicLab()

    model = IdealWorld(J, I, L)
    model.communicate_suspect_ids_and_crime_sample()
    model.get_profiles()
    model.find_DNA_similarities()
    model.find_DNA_matches(50)

    print(model.I.dna_matches)