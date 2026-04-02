% Inputs:
% p  - pressure time series (Pa)
% Fs - sampling frequency (Hz)

[x,y]=getlines;
time=x{1};
p=y{1};
Fs = 1/(time(2)-time(1))

p_ref = 20e-6;     % reference pressure (Pa)

N = length(p);
% optionally remove mean:
% p = p - mean(p);

% Choose Nfft (power of two often)
Nfft = 2^nextpow2(N);

% FFT
P = fft(p, Nfft);

% Frequency vector (positive)
f = (0:(Nfft/2))*(Fs/Nfft);

% Single-sided amplitude spectrum
% note: indices 1..Nfft/2+1 correspond to 0..Fs/2
A = (2/ Nfft) * abs(P(1:Nfft/2+1));
% correct DC and Nyquist (do not double DC)
A(1) = abs(P(1))/Nfft;
if rem(Nfft,2)==0
    A(end) = abs(P(Nfft/2+1))/Nfft; % Nyquist if present
end

% Convert peak amplitude to RMS
Prms = A ./ sqrt(2);

% Convert to SPL in dB (one value per frequency bin)
SPL = 20*log10( Prms / p_ref );

% Plot
figure;
plot(f, SPL,'r');
xlabel('Frequency (Hz)');
ylabel('SPL (dB re 20 \muPa)');
xlim([0 Fs/2]);
grid on;
