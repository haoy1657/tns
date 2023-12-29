import numpy as np
import ipywidgets as widgets
import pylab as plt
from scipy import signal


fs_default = 132300

class gui:
	def __init__(self, go_fct):

		def on_value_change_polynome(change):
			if self.polynome.value == "Butterworth" or self.polynome.value == "Bessel":
				self.ligne4.layout.visibility = 'hidden'
			else:
				self.ligne4.layout.visibility = 'visible'

		def on_value_change_nature(change):
			if self.nature.value == "RII":
				self.polynome.disabled = False
			else:
				self.polynome.disabled = True

		## ==== Fréquence d'échantillonnage
		self.fs = widgets.Text(
			value = str(fs_default),
			description = "Fe (Hz)",
			continuous_update = False,
		)

		## ==== RIF/RII
		self.nature = widgets.Dropdown(
    		options = ['RIF','RII'],
    		value = 'RIF',
    		description = 'Nature :',
    		continuous_update = False,
		)
		self.nature.observe(on_value_change_nature, names='value')

		## ==== Type de filtre
		self.type = widgets.Dropdown(
			options = ['Passe-Bas','Passe-Haut','Passe-Bande'],
			value = "Passe-Bas",
			description = "Type :",
			continuous_update = False,	
		)

		## ==== Ordre du filtre
		self.ordre = widgets.Text(
			value = "10",
			description = "Ordre",
			continuous_update = False,
		)

		## ==== Polynôme
		self.polynome = widgets.Dropdown(
			options = ['Butterworth','Chebyshev I','Chebyshev II','Elliptic','Bessel'],
			value = "Butterworth",
			description = "Polynôme :",
			disabled = True,
			continuous_update = False,	
		)
		self.polynome.observe(on_value_change_polynome, names='value')

		## ==== Fréquence(s) de coupure
		self.coupure = widgets.Text(
			value = "1000",
			description = "Fc (Hz)",
			continuous_update = False,
		)

		## ==== Ondulation dans la BP
		self.rp = widgets.Text(
			value = "1",
			description = "Rp (dB)",
			continuous_update = False,
		)

		## ==== Ondulation dans la BP
		self.rs = widgets.Text(
			value = "20",
			description = "Rs (dB)",
			continuous_update = False,
		)

		## ==== Bouton
		self.button = widgets.Button(
			description="Calcul",
		)
		self.button.on_click(go_fct)

		## === Description de l'interface
		self.ligne1 = widgets.HBox([self.fs])
		self.ligne2 = widgets.HBox([self.nature, self.ordre, self.polynome])
		self.ligne3 = widgets.HBox([self.type, self.coupure])
		self.ligne4 = widgets.HBox([self.rp, self.rs])
		self.ligne4.layout.visibility = 'hidden'
		self.cont = widgets.VBox([self.ligne1, self.ligne2, self.ligne3, self.ligne4, self.button])
			

class filtre():
	def __init__(self):
		self.gui = gui(self.update_plot)
		self.a = None
		self.b = None
		self.fs = fs_default

	def display(self, ax, fig):
		self.fig = fig
		self.ax = ax
		self.compute_filter()
		try:
			w, h = signal.freqz(self.b, self.a, worN=512, whole=False, plot=None, fs=self.fs)
		except:
			w, h = signal.freqz(self.b, self.a, worN=512, whole=False, plot=None)
			w = w * self.fs / np.pi
		self.fig = fig
		self.line0 = ax[0].semilogx(w,20*np.log10(np.abs(h)))
		self.ax[0].grid()
		self.ax[0].set_title('Gain')
		self.line1 = ax[1].plot(w,np.angle(h))
		self.ax[1].grid()
		self.ax[1].set_title('Phase')
		self.line2 = ax[2].scatter(self.b, np.zeros_like(self.b))
		self.ax[2].set_title('Pôles et zéros')
		self.ax[2].set_xlim(-1.5, 1.5)
		self.ax[2].set_ylim(-1.5, 1.5)
		self.ax[2].grid()
		display(self.gui.cont)

	def compute_filter(self):
		if self.gui.nature.value=='RIF':
			self.compute_filter_FIR()
		elif self.gui.nature.value=='RII':
			self.compute_filter_IIR()
		else:
			print("Nature du filtre non défini")	

	## ====== Computation of the FIR filter coefficients
	def compute_filter_FIR(self):
		# On récupère les éléments depuis le GUI
		ordre = int(self.gui.ordre.value)
		values = self.gui.coupure.value.split(",")
		fc = [float(i) for i in values]
		self.fs = float(self.gui.fs.value)

		## --- Filtre passe-haut
		if self.gui.type.value == "Passe-Haut":
			if len(fc)!=1:
				print("Fréquence de coupure mal saisie.")
				return
			try:
				self.b = signal.firwin(ordre+1, fc, fs=self.fs, pass_zero='highpass')
			except:
				self.b = signal.firwin(ordre+1, fc, fs=self.fs, pass_zero=False)
			
			# a est ajouté pour obtenir le filtre en z^-1
			self.a = np.concatenate([np.ones(1), np.zeros(len(self.b)-1)])
		
		## --- Filtre passe-bas
		elif self.gui.type.value == "Passe-Bas":
			if len(fc)!=1:
				print("Fréquence de coupure mal saisie.")
				return
			self.b = signal.firwin(ordre+1, fc, fs=self.fs)
			# a est ajouté pour obtenir le filtre en z^-1
			self.a = np.concatenate([np.ones(1), np.zeros(len(self.b)-1)])

		## --- Filtre passe-bande
		elif self.gui.type.value == "Passe-Bande":
			if len(fc)!=2:
				print("Fréquences de coupure mal saisies : pour le passe-bande, saisir 2 fréquences sous la forme fc1, fc2.")
				return

			try:
				self.b = signal.firwin(ordre+1, fc, fs=self.fs, pass_zero='bandpass')
			except: 
				self.b = signal.firwin(ordre+1, fc, fs=self.fs, pass_zero=False)

			self.a = np.concatenate([np.ones(1), np.zeros(len(self.b)-1)])
		
		else:
			print("Type de filtre non défini")

	## ====== Computation of the IIR filter coefficients
	def compute_filter_IIR(self):
		# On récupère les éléments depuis le GUI
		ordre = int(self.gui.ordre.value)
		values = self.gui.coupure.value.split(",")
		fc = [float(i) for i in values]
		self.fs = float(self.gui.fs.value)
		rp = float(self.gui.rp.value)
		rs = float(self.gui.rs.value)
		if self.gui.polynome.value == "Butterworth":
			poly = 'butter'
		elif self.gui.polynome.value == "Chebyshev I":
			poly = 'cheby1'
		elif self.gui.polynome.value == "Chebyshev II":
			poly = 'cheby2'
		elif self.gui.polynome.value == "Elliptic":
			poly = 'ellip'
		elif self.gui.polynome.value == "Bessel":
			poly = 'bessel'
		else:
			print("Mauvais choix du type de polynôme.")

		## --- Filtre passe-haut
		if self.gui.type.value == "Passe-Haut":
			if len(fc)!=1:
				print("Fréquence de coupure mal saisie.")
				return
			try:
				self.b, self.a = signal.iirfilter(ordre+1, Wn=fc, btype='highpass', analog=False, rp=rp, rs=rs, ftype=poly, fs=self.fs)
			except:
				self.b, self.a = signal.iirfilter(ordre+1, Wn=fc/self.fs, btype='highpass', analog=False, rp=rp, rs=rs, ftype=poly)

		## --- Filtre passe-bas
		elif self.gui.type.value == "Passe-Bas":
			if len(fc)!=1:
				print("Fréquence de coupure mal saisie.")
				return
			try:
				self.b, self.a = signal.iirfilter(ordre+1, Wn=fc, btype='lowpass', analog=False, rp=rp, rs=rs, ftype=poly, fs=self.fs)
			except:
				self.b, self.a = signal.iirfilter(ordre+1, Wn=fc/self.fs, btype='lowpass', analog=False, rp=rp, rs=rs, ftype=poly)

		## --- Filtre passe-bande
		elif self.gui.type.value == "Passe-Bande":
			if len(fc)!=2:
				print("Fréquences de coupure mal saisies : pour le passe-bande, saisir 2 fréquences sous la forme fc1, fc2.")
				return
			try:
				self.b, self.a = signal.iirfilter(ordre+1, Wn=fc, btype='bandpass', analog=False, rp=rp, rs=rs, ftype=poly, fs=self.fs)
			except:
				self.b, self.a = signal.iirfilter(ordre+1, Wn=fc/self.fs, btype='bandpass', analog=False, rp=rp, rs=rs, ftype=poly)
			
		else:
			print("Type de filtre non défini")

	## ====== Impulse response computation
	def impulse_response(self, length=None):
		system = (self.b, self.a, 1/self.fs)
		t, rep = signal.dimpulse(system, n=length)
		n = np.arange(0, len(t))
		rep_imp = np.squeeze(rep)
		return (n, rep_imp)

	## ====== Step response computation
	def step_response(self, length=None):
		system = (self.b, self.a, 1/self.fs)
		t, rep = signal.dstep(system, n=length)
		n = np.arange(0, len(t))
		rep_step = np.squeeze(rep)
		return rep_step

	## ====== Filter computation
	def filter(self, x):
		y = signal.lfilter(self.b, self.a, x)
		n = np.arange(0,len(y))
		return (n, y)

	def update_plot(self,b):
		#print("update_plot")
		self.compute_filter()
		try:
			w, h = signal.freqz(self.b, self.a, worN=512, whole=False, plot=None, fs=self.fs)
		except:
			w, h = signal.freqz(self.b, self.a, worN=512, whole=False, plot=None)
			w = w * self.fs / np.pi
		self.ax[0].cla()
		self.ax[1].cla()
		self.ax[2].cla()
		self.ax[0].set_title('Gain (dB)')
		self.ax[1].set_title('Phase (deg)')
		self.ax[2].set_title('Pôles et zéros')
		plt.autoscale(True)
		self.line0 = self.ax[0].semilogx(w,20*np.log10(np.abs(h)))
		self.ax[0].grid()
		self.line1 = self.ax[1].plot(w,np.unwrap(np.angle(h)))
		self.ax[1].grid()
		zeros = np.roots(self.b)
		poles = np.roots(self.a)
		circle = plt.Circle((0, 0), 1, color='r', fill=False)
		self.line21 = self.ax[2].add_artist(circle)
		self.line22 = self.ax[2].scatter(np.real(zeros), np.imag(zeros), label="zéros")
		self.line23 = self.ax[2].scatter(np.real(poles), np.imag(poles), marker="x", label="pôles")
		self.ax[2].set_aspect('equal')
		self.ax[2].set_xlim(-1.5, 1.5)
		self.ax[2].set_ylim(-1.5, 1.5)
		self.ax[2].grid()
		plt.legend()
