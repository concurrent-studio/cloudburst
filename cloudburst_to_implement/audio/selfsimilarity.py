# -*- coding: utf-8 -*-
import codecs
import json
import librosa
import numpy as np
from glob import glob
from numba import njit
import matplotlib
import matplotlib.pyplot as plt

# Don't stop process if division by 0 is present
np.seterr(divide='ignore', invalid='ignore')

# Plot and save
def plot(matrix, filename="tmp"):
  fig, ax = plt.subplots(figsize=(10, 10))
  im = ax.imshow(matrix)
  ax.set_title(filename)
  fig.tight_layout()
  plt.savefig('{}.png'.format(filename))
  plt.close()

@njit(parallel=True)
def self_sim(a, window_length=1800, sliding_window=True, slide_length=2205):
  """Generate self-similarity matrix given any time series 'a' """
  # Flatten incoming array to ensure it is one dimensional
  a = a.flatten()
  # If a sliding window is not selected, set the slide length to the window length
  slide_length = window_length if not sliding_window else slide_length

  # Segment list according to window_length and slide_length
  s = np.array([np.float64(x) for x in range(0)])
  for i in range(0, a.shape[0]-window_length, slide_length):
    s = np.append(s, np.asarray(a[i:i+window_length]))
  s = np.reshape(s, (s.shape[0]//window_length, window_length))
  
  # Iterate through each chunk, gathering its correlation to each other chunk
  m = np.array([np.float64(x) for x in range(0)])
  for i in range(s.shape[0]):
    for j in range(s.shape[0]):
      m = np.append(m, np.corrcoef(s[i], s[j])[1,0])

  # Return properly shaped self-similarity matrix
  return m.reshape(s.shape[0], s.shape[0])

@njit(parallel=True)
def mb_np(m):
  # Normalize matrix heights to match matrix dimensions
  m = min(m.shape) * m

  # Iterate greatest grid of box sizes at a power of 2 <= matrix's dimensions
  n = int(np.floor(np.log(min(m.shape))/np.log(2)))  
  
  # Count boxes
  bc_s = []
  # Iterate through grid sizes
  for b in  2**np.arange(n, 1, -1):
    bc = 0
    # Z direction in box grid
    for z in range(0, 2**n, b):
      # X, Y direction in box grid
      for x in range(0, 2**n, b):
        # Increment box count if any of voxes is full
        bc += 1 if (m[x:x+b, x:x+b] >= z).sum() > 0 else 0
    bc_s.append(bc)
  
  return n, bc_s

def mb(m):
  """ Extension of mb_np func, containing features not allowed by @njit """
  n, bc_s = mb_np(m)
  try:
    c = np.polyfit(np.log(2**np.arange(n, 1, -1)), np.log(bc_s), 1)
    return -c[0]
  
  except:
    print("POLYFIT ERROR")
    return None

def main(wav):
  y, sr = librosa.load(wav)
  filename = wav.split("/")[-1].split(".")[0]
  print("{} | Sample length = {} sec, {} samples. Sample rate = {}.".format(filename, round(y.size/sr, 3), y.size, sr))
  
  # Gather audio features
  stft = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
  chroma = librosa.feature.chroma_stft(y=y, sr=sr)
  mfcc = librosa.feature.mfcc(y=y, sr=sr)
  tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
  zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
  rms = librosa.feature.rms(y=y)
  spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
  spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
  tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

  # Generate self similarity matrices from audio features
  # S-Matrix
  s_m = np.nan_to_num(self_sim(stft))

  # Autocorrelation Matrix
  ac_m = np.nan_to_num(self_sim(y))
  
  # Chroma matrices
  chroma_m_c = np.nan_to_num(self_sim(chroma[0], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_csharp = np.nan_to_num(self_sim(chroma[1], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_d = np.nan_to_num(self_sim(chroma[2], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_dsharp = np.nan_to_num(self_sim(chroma[3], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_e = np.nan_to_num(self_sim(chroma[4], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_f = np.nan_to_num(self_sim(chroma[5], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_fsharp = np.nan_to_num(self_sim(chroma[6], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_g = np.nan_to_num(self_sim(chroma[7], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_gsharp = np.nan_to_num(self_sim(chroma[8], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_a = np.nan_to_num(self_sim(chroma[9], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_asharp = np.nan_to_num(self_sim(chroma[10], window_length=10, sliding_window=True, slide_length=8))
  chroma_m_b = np.nan_to_num(self_sim(chroma[11], window_length=10, sliding_window=True, slide_length=8))
  
  # MFCC Matrices
  mfcc_m0 = np.nan_to_num(self_sim(mfcc[0], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m1 = np.nan_to_num(self_sim(mfcc[1], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m2 = np.nan_to_num(self_sim(mfcc[2], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m3 = np.nan_to_num(self_sim(mfcc[3], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m4 = np.nan_to_num(self_sim(mfcc[4], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m5 = np.nan_to_num(self_sim(mfcc[5], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m6 = np.nan_to_num(self_sim(mfcc[6], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m7 = np.nan_to_num(self_sim(mfcc[7], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m8 = np.nan_to_num(self_sim(mfcc[8], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m9 = np.nan_to_num(self_sim(mfcc[9], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m10 = np.nan_to_num(self_sim(mfcc[10], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m11 = np.nan_to_num(self_sim(mfcc[11], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m12 = np.nan_to_num(self_sim(mfcc[12], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m13 = np.nan_to_num(self_sim(mfcc[13], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m14 = np.nan_to_num(self_sim(mfcc[14], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m15 = np.nan_to_num(self_sim(mfcc[15], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m16 = np.nan_to_num(self_sim(mfcc[16], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m17 = np.nan_to_num(self_sim(mfcc[17], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m18 = np.nan_to_num(self_sim(mfcc[18], window_length=10, sliding_window=True, slide_length=8))
  mfcc_m19 = np.nan_to_num(self_sim(mfcc[19], window_length=10, sliding_window=True, slide_length=8))
  
  # Tonnetz Self Similarity Matrices
  tonnetz_m5x = np.nan_to_num(self_sim(tonnetz[0], window_length=10, sliding_window=True, slide_length=8))
  tonnetz_m5y = np.nan_to_num(self_sim(tonnetz[1], window_length=10, sliding_window=True, slide_length=8))
  tonnetz_mmx = np.nan_to_num(self_sim(tonnetz[2], window_length=10, sliding_window=True, slide_length=8))
  tonnetz_mmy = np.nan_to_num(self_sim(tonnetz[3], window_length=10, sliding_window=True, slide_length=8))
  tonnetz_mMx = np.nan_to_num(self_sim(tonnetz[4], window_length=10, sliding_window=True, slide_length=8))
  tonnetz_mMy = np.nan_to_num(self_sim(tonnetz[5], window_length=10, sliding_window=True, slide_length=8))

  zero_crossing_rate_m = np.nan_to_num(self_sim(zero_crossing_rate, window_length=10, sliding_window=True, slide_length=8))
  rms_m = np.nan_to_num(self_sim(rms, window_length=10, sliding_window=True, slide_length=8))
  spectral_centroid_m = np.nan_to_num(self_sim(spectral_centroid, window_length=10, sliding_window=True, slide_length=8))
  spectral_rolloff_m = np.nan_to_num(self_sim(spectral_rolloff, window_length=10, sliding_window=True, slide_length=8))
  beats_m = np.nan_to_num(self_sim(beats, window_length=4, sliding_window=True, slide_length=3))

  # Save Plots
  plot(s_m, filename + " S-Matrix")
  plot(ac_m, filename + " Autocorrelation Matriz")
  plot(chroma_m_c, filename + " Chroma C Matrix")
  plot(chroma_m_csharp, filename + " Chroma C# Matrix")
  plot(chroma_m_d, filename + " Chroma D Matrix")
  plot(chroma_m_dsharp, filename + " Chroma D# Matrix")
  plot(chroma_m_e, filename + " Chroma E Matrix")
  plot(chroma_m_f, filename + " Chroma F Matrix")
  plot(chroma_m_fsharp, filename + " Chroma F# Matrix")
  plot(chroma_m_g, filename + " Chroma G Matrix")
  plot(chroma_m_gsharp, filename + " Chroma G# Matrix")
  plot(chroma_m_a, filename + " Chroma A Matrix")
  plot(chroma_m_asharp, filename + " Chroma A# Matrix")
  plot(chroma_m_b, filename + " Chroma B Matrix")
  plot(mfcc_m0, filename + " MFCC 0 Matrix")
  plot(mfcc_m1, filename + " MFCC 1 Matrix")
  plot(mfcc_m2, filename + " MFCC 2 Matrix")
  plot(mfcc_m3, filename + " MFCC 3 Matrix")
  plot(mfcc_m4, filename + " MFCC 4 Matrix")
  plot(mfcc_m5, filename + " MFCC 5 Matrix")
  plot(mfcc_m6, filename + " MFCC 6 Matrix")
  plot(mfcc_m7, filename + " MFCC 7 Matrix")
  plot(mfcc_m8, filename + " MFCC 8 Matrix")
  plot(mfcc_m9, filename + " MFCC 9 Matrix")
  plot(mfcc_m10, filename + " MFCC 10 Matrix")
  plot(mfcc_m11, filename + " MFCC 11 Matrix")
  plot(mfcc_m12, filename + " MFCC 12 Matrix")
  plot(mfcc_m13, filename + " MFCC 13 Matrix")
  plot(mfcc_m14, filename + " MFCC 14 Matrix")
  plot(mfcc_m15, filename + " MFCC 15 Matrix")
  plot(mfcc_m16, filename + " MFCC 16 Matrix")
  plot(mfcc_m17, filename + " MFCC 17 Matrix")
  plot(mfcc_m18, filename + " MFCC 18 Matrix")
  plot(mfcc_m19, filename + " MFCC 19 Matrix")
  plot(tonnetz_m5x, filename + " Tonnetz m5x Matrix")
  plot(tonnetz_m5y, filename + " Tonnetz m5y Matrix")
  plot(tonnetz_mmx, filename + " Tonnetz mmx Matrix")
  plot(tonnetz_mmy, filename + " Tonnetz mmy Matrix")
  plot(tonnetz_mMx, filename + " Tonnetz mMx Matrix")
  plot(tonnetz_mMy, filename + " Tonnetz mMy Matrix")
  plot(zero_crossing_rate_m, filename + " Zero Crossing Rate Matrix")
  plot(rms_m, filename + " RMS Matrix")
  plot(spectral_centroid_m, filename + " Spectral Centroid Matrix")
  plot(spectral_rolloff_m, filename + " Spectral Rolloff Matrix")
  plot(beats_m, filename + " Beats Matrix")

  # Analyze Minkowski–Bouligand dimension of features
  s_mb = mb(s_m)
  ac_mb = mb(ac_m)
  chroma_c_mb = mb(chroma_m_c)
  chroma_csharp_mb = mb(chroma_m_csharp)
  chroma_d_mb = mb(chroma_m_d)
  chroma_dsharp_mb = mb(chroma_m_dsharp)
  chroma_e_mb = mb(chroma_m_e)
  chroma_f_mb = mb(chroma_m_f)
  chroma_fsharp_mb = mb(chroma_m_fsharp)
  chroma_g_mb = mb(chroma_m_g)
  chroma_gsharp_mb = mb(chroma_m_gsharp)
  chroma_a_mb = mb(chroma_m_a)
  chroma_asharp_mb = mb(chroma_m_asharp)
  chroma_b_mb = mb(chroma_m_b)
  mfcc_0_mb = mb(mfcc_m0)
  mfcc_1_mb = mb(mfcc_m1)
  mfcc_2_mb = mb(mfcc_m2)
  mfcc_3_mb = mb(mfcc_m3)
  mfcc_4_mb = mb(mfcc_m4)
  mfcc_5_mb = mb(mfcc_m5)
  mfcc_6_mb = mb(mfcc_m6)
  mfcc_7_mb = mb(mfcc_m7)
  mfcc_8_mb = mb(mfcc_m8)
  mfcc_9_mb = mb(mfcc_m9)
  mfcc_10_mb = mb(mfcc_m10)
  mfcc_11_mb = mb(mfcc_m11)
  mfcc_12_mb = mb(mfcc_m12)
  mfcc_13_mb = mb(mfcc_m13)
  mfcc_14_mb = mb(mfcc_m14)
  mfcc_15_mb = mb(mfcc_m15)
  mfcc_16_mb = mb(mfcc_m16)
  mfcc_17_mb = mb(mfcc_m17)
  mfcc_18_mb = mb(mfcc_m18)
  mfcc_19_mb = mb(mfcc_m19)
  tonnetz_m5x_mb = mb(tonnetz_m5x)
  tonnetz_m5y_mb = mb(tonnetz_m5y)
  tonnetz_mmx_mb = mb(tonnetz_mmx)
  tonnetz_mmy_mb = mb(tonnetz_mmy)
  tonnetz_mMx_mb = mb(tonnetz_mMx)
  tonnetz_mMy_mb = mb(tonnetz_mMy)
  zero_crossing_rate_mb = mb(zero_crossing_rate_m)
  rms_mb = mb(rms_m)
  spectral_centroid_mb = mb(spectral_centroid_m)
  spectral_rolloff_mb = mb(spectral_rolloff_m)
  beats_mb = mb(beats_m)

  #  Save features in JSON file
  data = {}
  data["stdanalysis"] = []
  data["stdanalysis"].append({
      'stft': stft.tolist(),
      'chroma': chroma.tolist(),
      'mfcc': mfcc.tolist(),
      'tonnetz': tonnetz.tolist(),
      'zero crossing rate': zero_crossing_rate.tolist(),
      'rms': rms.tolist(),
      'spectral centroid': spectral_centroid.tolist(),
      'spectral rolloff': spectral_rolloff.tolist(),
      'beats': beats.tolist()
  })
  data["ssmatrices"] = []
  data["ssmatrices"].append({
      's-matrix': s_m,
      'autocorrelation matrix': ac_m,
      'chroma c matrix': chroma_m_c,
      'chroma c# matrix': chroma_m_csharp,
      'chroma d matrix': chroma_m_d,
      'chroma d# matrix': chroma_m_dsharp,
      'chroma e matrix': chroma_m_e,
      'chroma f matrix': chroma_m_f,
      'chroma f# matrix': chroma_m_fsharp,
      'chroma g matrix': chroma_m_g,
      'chroma g# matrix': chroma_m_gsharp,
      'chroma a matrix': chroma_m_a,
      'chroma a# matrix': chroma_m_asharp,
      'chroma b matrix': chroma_m_b,
      'mfcc 0 matrix': mfcc_m0,
      'mfcc 1 matrix': mfcc_m1,
      'mfcc 2 matrix': mfcc_m2,
      'mfcc 3 matrix': mfcc_m3,
      'mfcc 4 matrix': mfcc_m4,
      'mfcc 5 matrix': mfcc_m5,
      'mfcc 6 matrix': mfcc_m6,
      'mfcc 7 matrix': mfcc_m7,
      'mfcc 8 matrix': mfcc_m8,
      'mfcc 9 matrix': mfcc_m9,
      'mfcc 10 matrix': mfcc_m10,
      'mfcc 11 matrix': mfcc_m11,
      'mfcc 12 matrix': mfcc_m12,
      'mfcc 13 matrix': mfcc_m13,
      'mfcc 14 matrix': mfcc_m14,
      'mfcc 15 matrix': mfcc_m15,
      'mfcc 16 matrix': mfcc_m16,
      'mfcc 17 matrix': mfcc_m17,
      'mfcc 18 matrix': mfcc_m18,
      'mfcc 19 matrix': mfcc_m19,
      'tonnetz m5x matrix': tonnetz_m5x,
      'tonnetz m5y matrix': tonnetz_m5y,
      'tonnetz mmx matrix': tonnetz_mmx,
      'tonnetz mmy matrix': tonnetz_mmy,
      'tonnetz mMx matrix': tonnetz_mMx,
      'tonnetz mMy matrix': tonnetz_mMy,
      'zero crossing rate matrix': zero_crossing_rate_m,
      'rms matrix': rms_mb,
      'spectral centroid matrix': spectral_centroid_m,
      'spectral rolloff matrix': spectral_rolloff_m,
      'beats matrix': beats_m,
  })
  data["minkowski bouligand"] = []
  data["minkowski bouligand"].append({
      's-matrix': s_mb,
      'autocorrelation matrix': ac_mb,
      'chroma c matrix': chroma_c_mb,
      'chroma c# matrix': chroma_csharp_mb,
      'chroma d matrix': chroma_d_mb,
      'chroma d# matrix': chroma_dsharp_mb,
      'chroma e matrix': chroma_e_mb,
      'chroma f matrix': chroma_f_mb,
      'chroma f# matrix': chroma_fsharp_mb,
      'chroma g matrix': chroma_g_mb,
      'chroma g# matrix': chroma_gsharp_mb,
      'chroma a matrix': chroma_a_mb,
      'chroma a# matrix': chroma_asharp_mb,
      'chroma b matrix': chroma_b_mb,
      'mfcc 0 matrix': mfcc_0_mb,
      'mfcc 1 matrix': mfcc_1_mb,
      'mfcc 2 matrix': mfcc_2_mb,
      'mfcc 3 matrix': mfcc_3_mb,
      'mfcc 4 matrix': mfcc_4_mb,
      'mfcc 5 matrix': mfcc_5_mb,
      'mfcc 6 matrix': mfcc_6_mb,
      'mfcc 7 matrix': mfcc_7_mb,
      'mfcc 8 matrix': mfcc_8_mb,
      'mfcc 9 matrix': mfcc_9_mb,
      'mfcc 10 matrix': mfcc_10_mb,
      'mfcc 11 matrix': mfcc_11_mb,
      'mfcc 12 matrix': mfcc_12_mb,
      'mfcc 13 matrix': mfcc_13_mb,
      'mfcc 14 matrix': mfcc_14_mb,
      'mfcc 15 matrix': mfcc_15_mb,
      'mfcc 16 matrix': mfcc_16_mb,
      'mfcc 17 matrix': mfcc_17_mb,
      'mfcc 18 matrix': mfcc_18_mb,
      'mfcc 19 matrix': mfcc_19_mb,
      'tonnetz m5x matrix': tonnetz_m5x_mb,
      'tonnetz m5y matrix': tonnetz_m5y_mb,
      'tonnetz mmx matrix': tonnetz_mmx_mb,
      'tonnetz mmy matrix': tonnetz_mmy_mb,
      'tonnetz mMx matrix': tonnetz_mMx_mb,
      'tonnetz mMy matrix': tonnetz_mMy_mb,
      'zero crossing rate matrix': zero_crossing_rate_mb,
      'rms matrix': rms_mb,
      'spectral centroid matrix': spectral_centroid_mb,
      'spectral rolloff matrix': spectral_rolloff_mb,
      'beats matrix': beats_mb,
  })

  try:
    json.dump(data, codecs.open('{}.json'.format(filename), 'w', encoding='utf-8'), separators=(',', ':'), indent=4) 
  except:
    print("JSON DUMP ERROR")

# Analyze each file
for wav in glob('./*.wav'):
  main(wav)
