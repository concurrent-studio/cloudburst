from pylab import * # import matlab-like plotting and numerical functions
rcParams['figure.figsize']=(12,6) # Set the detault size for figures to large

def dissonance(freqs, amps=None, params=None):
    """                                                                                                                             
    Compute dissonance between partials with center frequencies in freqs, uses a model of critical bandwidth.                                                     
    and amplitudes in amps. Based on Sethares "Tuning, Timbre, Spectrum, Scale" (1998) after Plomp and Levelt (1965)                                                 
    
    inputs:
        freqs - list of partial frequencies
        amps - list of corresponding amplitudes [default, uniformly 1]
    """
    if params == None: params = (-3.51, -5.75, 0.0207, 19.96, 5, -5, 0.24)
    b1, b2, s1, s2, c1, c2, Dstar  = params
    f = array(freqs).flatten() # flatten to cope with lists of lists
    if amps is None: amps = [1]*len(f)
    a = array(amps).flatten()
    idx = argsort(f)
    f = f[idx]
    a = a[idx]
    N = f.size
    D = 0
    for i in range(1, N):
        Fmin = f[ 0 : N - i ]
        S = Dstar / ( s1 * Fmin + s2)
        Fdif = f[ i : N ] - f[ 0 : N - i ]
        am = a[ i : N ] * a[ 0 : N - i ]
        Dnew = am * (c1 * exp (b1 * S * Fdif) + c2 * exp(b2 * S * Fdif))
        D += Dnew.sum()
    return D

##############

f0 = 440 # This is the frequency of 'concert A'

# To use the dissonance function, we supply a list of frequencies
# Here, we use f0 and 2*f0, corresponding to two frequency components an octave apart
dissonance( [f0, 2*f0] )

# The answer should be close to zero, since an octave is a consonant pitch interval (but not zero, because that is reserved for the unison)

##############

# Calculate the dissonance function for the interval of a perfect fifth, which is 3/2 or 1.5 * f0
dissonance( [f0, 1.5*f0] )

##############

# Calculate dissonance for 12 equal-temperament tuning frequencies in the range of an octave
ratios = logspace(0, log10(2), 24) # Generates a list of equal-temperament frequency ratios 
print ratios

##############

# Now apply the dissonacne function for each of the quarter-tone equal temperament ratios 
# for a fundamental frequency of 55Hz
f0 = 110 # Fundamental Frequency
plot( [dissonance([f0, f0*r]) for r in ratios] ) # plot dissonance for pair-wise tones between f0 and all ratios
xlabel('1/4-tone interval')
ylabel('dissonance')
t=title('Dissonance function at %dHz'%f0)

##############

# Capture the output as a list and plot the result
f0 = 110 
curve = [dissonance([f0, f0*r]) for r in ratios]

# Plot the dissonance curve
freqs = f0 * ratios
plot(freqs, curve)
stem(freqs, curve)
title('Dissonance of simple tones within one octave at %d Hz'%f0)
xlabel('Frequency (Hz)')
ylabel('dissonance')

################

# The x-axis above was in frequency
# Let's see that again, but as musical intervals
# The intervals are 1/4 tones within an octave (2 x 1/4 tone = 1/2 step)
f0 = 110 
curve = [dissonance([f0, f0*r]) for r in ratios]

intervals = arange(24)
plot(intervals, curve)
stem(intervals, curve)
xlabel('Interval (quarter tones)')
ylabel('dissonance')
t=title('Dissonance in 1/4-tones within one octave at %d Hz'%f0)

#################

# Now, let's plot the same curve at different frequencies

for f0 in [110, 220, 440, 880]:
    curve = [dissonance([f0, f0*r]) for r in ratios]
    plot(curve)
legend(['110Hz','220Hz','440Hz','880Hz'])
t=title('Dissonance within one octave, multiple f0')

#################

# Compute the dissonance for a tone with 6 harmonics 
# This sums all of the dissonances within the tone
f0 = 440
freqs0 = arange(1,7) * f0 # six harmonics beginning at f0
amps0 = exp(-0.5*arange(1,7))

stem(freqs0, amps0)
title('Complex tone spectrum, f0=%dHz'%f0)
xlabel('Frequency (Hz)')
ylabel('Amplitude')
print "Dissonance =", dissonance(freqs0, amps0)

# Plot the waveform corresponding to this spectrum (assume zero-phase)
figure()
x = zeros(512)
for f,a in zip(freqs0, amps0):
    x += a*cos(2*pi*f*arange(512)/48000.0)
plot(x)
xlabel('Sample index (sr=48000Hz)')
ylabel('amplitude')
t=title('Complex tone waveform')

######################

# Make a second complex tone at the interval of a fifth from the first
# And plot the spectra of the two tones
f1 = f0 * 1.5 # A Perfect fifth
freqs1 = arange(1,7) * f1 # six harmonics beginning at f0
amps1 = exp(-0.5*arange(1,7))

stem(freqs0,amps0,'gs-') # Colored stem plots
stem(freqs1,amps1,'mo-')
xlabel('Frequency (Hz)')
ylabel('Amplitude')
legend(['440Hz Tone','660Hz Tone'])
t=title('Spectra of complex tones, f0=%.2fHz, f1=%.2fHz'%(f0,f1))

#####################

# Compute the dissonance between the two tones f0 and f1 (with amplitudes freqs1 and amps1)
dissonance([freqs0, freqs1],[amps0, amps1])

#####################

# Compute dissonance between two complex tones with fundamental frequencies f0 and f1 
# for a sweep of the upper tone over an octave

ratios = logspace(0, log10(2), 96) # sixteenth-tone frequency ratio spacing (for better resolution)
df = [dissonance([freqs0, arange(1,7)*f0*r]) for r in ratios]
plot(f0*ratios,df)
grid()
xlabel('Frequency (Hz)')
ylabel('Dissonance')

# Plot with exponentially weight amplitudes
amps2 = exp(-0.1*arange(1,7))
df2 = [dissonance([freqs0, arange(1,7)*f0*r],[amps2,amps2]) for r in ratios]
plot(f0*ratios,df2)

amps3 = exp(-0.25*arange(1,7))
df3 = [dissonance([freqs0, arange(1,7)*f0*r],[amps3,amps3]) for r in ratios]
plot(f0*ratios,df3)

legend(['amps=1','amps=exp(-0.1*k)','amps=exp(-0.25*k)'])
t = title('Dissonance of 2 complex tones (f0,f1) f1 swept over an octave')

#####################

# Label the positions of intervals M2, M3, P4, P5, M6, M7, and P8 on the following graph
ratios = logspace(0, log10(2), 96) # sixteenth-tone frequency ratio spacing (for better resolution)
df = [dissonance([freqs0, arange(1,7)*f0*r]) for r in ratios]
plot(f0*ratios,df)
grid()
xlabel('Frequency (Hz)')
ylabel('Dissonance')

# HINT: Here is the label for the first interval (Unison: f1 = 1*f0
plot([1*f0,1*f0],[0,6],'--') # Make a dashed vertical line
text(1*f0, 5.5, 'P1', fontsize=14) # Write a text label

# COMPLETE FOR ALL 7 INTERVALS M2, M3, P4, P5, M6, M7, and P8 
# Use the hint on the two lines above.

t=title('Interval positions on the dissonance curve')

#########################

Prelude01 = loadtxt('BachWTC1/01.ascii') # WTC Book 1, Prelude in C Major
# Inspect the array by checking its size
Prelude01.shape

######################

# Look at the data (To much data to see in text form)
Prelude01

#####################

# Make a function to sensibly plot these files
def show_score(S):
    imshow(S, aspect='auto', origin='bottom', interpolation='nearest', cmap=cm.gray_r)
    xlabel('Time')
    ylabel('Pitch')
    pc=array(['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B'])
    idx = tile([0,4,7],13)[:128]
    yticks(arange(0,128,4),pc[idx], fontsize=10)

#####################

show_score(Prelude01)
ylabel('Pitch')
xlabel('Time index')
t=title('J. S. Bach, Prelude No. 1 in C Major')

##################

# The following function allows us to compute dissonance over the whole score
def dissonance_score(A):
    """                                                                                                                              
    Given a piano-roll indicator matrix representation of a musical work (128 pitches x beats),                                      
    return the dissonance as a function of beats.                                                                                    
    Input:                                                                                                                           
        A  - 128 x beats indicator matrix of MIDI pitch number                                                                       
                                                                                                                                     
    """
    freq_rats = arange(1,11) # Harmonic series ratios                                                                             
    amps = exp(-.5 * freq_rats) # Partial amplitudes                                                                              
    F0 = 8.1757989156 # base frequency for MIDI (note 0)                                                                             
    diss = [] # List for dissonance values                                                                                           
    thresh = 1e-3
    for beat in A.T:
        idx = where(beat>thresh)[0]
        if len(idx):
            freqs, mags = [], [] # lists for frequencies, mags                                                                       
            for i in idx:
                freqs.extend(F0*2**(i/12.0)*freq_rats)
                mags.extend(amps)
            freqs = array(freqs)
            mags = array(mags)
            sortIdx = freqs.argsort()
            d = dissonance(freqs[sortIdx],mags[sortIdx])
            diss.extend([d])
        else:
            diss.extend([-1]) # Null value                                                                                           
    return array(diss)

#################

plot(dissonance_score(Prelude01))
xlabel('Time index')
ylabel('Dissonance')
t=title('Dissonance over the whole of WTC Prelude 1 (raw / unsmoothed)')

#################

# The above dissonance plot is not smooth because the time-scale of the analysis is 1/8th notes; 
# hence, the dissonance function changes non-smoothly on every beat. 
#
# The following function will smooth the score by temporally integrating the score matrix over a fixed number of beats.
def win_mtx(a, win_len=8):
    """                                                                                                                              
    Options:                                                                                                                         
        win_len  - window length [8]                                                                                                 
    """
    # perform simple integration                                                                                                     
    N = int(ceil(a.shape[1]/float(win_len)))
    aa = []
    for k in arange(N-1):
        aa.append(a[:,k*win_len:(k+1)*win_len].mean(1)) # temporally integrate by teking the mean of axis 1
    return vstack(aa).T

###############

# Now we can smooth the score using win_mtx
# Each bar consists of a repeated pitch pattern of one chord
# The pulse is 1/8th note (the smallest duration used in the work)
# So, we integrate over 8 pulses, the length of one bar
Prelude01_integrated = win_mtx(Prelude01, 8)

show_score(Prelude01_integrated)
xlabel('Bar')
ylabel('Pitch')
t=title('J. S. Bach Prelude No. 1 Temporal Integration')

figure()
plot(dissonance_score(Prelude01_integrated))
xlabel('Bar')
ylabel('Dissonance')
grid()
t=title('J. S. Bach Prelude No. 1 Dissonance (Temporally Integrated)')

################

# Let's look at the Fugue in C Major in the same way
# Step 1: Load the ASCII file corresponding to Fugure No. 1 = 02.ascii
# Step 2: Smooth the score using win_mtx, the pulse is 1/32nd note
#         The "harmonic rate" is faster in the Fugue than the Prelude, with chords changing every quarter note
#         so we integrate over 8 x 1/32nd notes which yields smoothing at the quarter-note level (32/8 = 4) 
# Step 3: Compute the dissonance

Fugue01 = loadtxt('BachWTC1/02.ascii') # WTC Book 1, Fugue in C Major
Fugue01_integrated = win_mtx(Fugue01, 8) # Integrate to quarter notes (pulse is 1/32nd note)
Fugue01_dissonance = dissonance_score(Fugue01_integrated)

figure()
show_score(Fugue01[:,:64]) # Just show the first two bars (64 x 1/32 note)
xlabel('Beat (1/8th Notes)')
ylabel('Pitch')
title('J. S. Bach Fugue No. 1 in C Major')

figure()
show_score(Fugue01_integrated[:,:8]) # Show the first two bars (8 x 1/4 notes)
xlabel('Beat (1/4 Notes)')
ylabel('Pitch')
title('J. S. Bach Fugue No. 1 in C Major (Temporally Integrated)')

figure()
plot(Fugue01_dissonance)
xlabel('Beat (1/4 Notes)')
ylabel('Dissonance')
grid()
axis('tight') # Remove blank space in figure
t = title('J. S. Bach Fugue No. 1 Dissonance (Temporally Integrated)')

##############

