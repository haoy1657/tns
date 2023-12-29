from scipy import signal
import numpy as np


def demultiplex(stereo, FILTRE1, FILTRE2):

	# Pour commencer, on récupère le signgal G+D
	n, g_plus_d = FILTRE1.filter(stereo)

	# Puis on extrait la porteuse
	n, porteuse19k = FILTRE2.filter(stereo)

	# On met la porteuse au carré
	porteuse19k2 = np.square(porteuse19k)

	# Puis on filtre passe-bande
	ordre = 25
	fc = 30000,50000
	try: 
		b = signal.firwin(ordre+1, fc, fs=FILTRE1.fs, pass_zero='bandpass')
	except:
		b = signal.firwin(ordre+1, fc, fs=FILTRE1.fs, pass_zero=False)
	
	a = np.concatenate([np.ones(1), np.zeros(len(b)-1)])
	porteuse38k = 200*signal.lfilter(b, a, porteuse19k2)

	# On récupère le signal G-D autour de 38kHz
	ordre = 50
	fc = (23000, 53000)
	try:
		b = signal.firwin(ordre+1, fc, fs=FILTRE1.fs, pass_zero='bandpass')
	except:
		b = signal.firwin(ordre+1, fc, fs=FILTRE1.fs, pass_zero=False)
	
	a = np.concatenate([np.ones(1), np.zeros(len(b)-1)])
	signal_module = signal.lfilter(b, a, stereo)

	# Et on le multiplie par la porteuse à 38k
	signal_module_product = np.multiply(signal_module, porteuse38k)

	# Enfin, On filtre passe-bas le résultat
	ordre = 50
	fc = 20000
	b = signal.firwin(ordre+1, fc, fs=FILTRE1.fs)
	a = np.concatenate([np.ones(1), np.zeros(len(b)-1)])
	g_moins_d = 2*signal.lfilter(b, a, signal_module_product)

	return n, g_plus_d, g_moins_d