
[x,y]=getlines;
time=x{1};
p=y{1};
Fs = 1/(time(2)-time(1))


% Inputs:
% p  - pressure time series (Pa)
% Fs - sampling frequency (Hz)
p_ref = 20e-6;     % reference pressure (Pa)

N = length(p);
p = p - mean(p);
Nfft = 2^nextpow2(N);

P = fft(p, Nfft);
f = (0:(Nfft/2))*(Fs/Nfft);

A = (2/ Nfft) * abs(P(1:Nfft/2+1));
A(1) = abs(P(1))/Nfft;
if rem(Nfft,2)==0
    A(end) = abs(P(Nfft/2+1))/Nfft; % Nyquist correction
end

Prms = A ./ sqrt(2);
SPL = 20*log10( Prms / p_ref );

%% --- A-weighting curve (IEC 61672) ---
fA = f;
Ra = (12200^2 * fA.^4) ./ ...
    ((fA.^2 + 20.6^2) .* sqrt((fA.^2 + 107.7^2) .* (fA.^2 + 737.9^2)) .* (fA.^2 + 12200^2));
A_weight = 20*log10(Ra) + 2.00;  % dB
SPL_A = SPL + A_weight;

%% --- Overall A-weighted SPL ---
df = Fs/Nfft;
pA_linear = (Prms .* 10.^(A_weight/20)).^2;
pA_total_rms = sqrt(sum(pA_linear) * df);
SPL_A_total = 20*log10(pA_total_rms / p_ref);
fprintf('Overall A-weighted SPL = %.2f dBA\n', SPL_A_total);

%% --- 1/3-Octave Band Analysis (A-weighted) ---
% ISO/IEC standard nominal band centers (Hz)
f_center = [ ...
   12.5 16 20 25 31.5 40 50 63 80 100 125 160 200 250 315 400 500 ...
   630 800 1000 1250 1600 2000 2500 3150 4000 5000 6300 8000 10000 12500 16000 20000];

nBands = length(f_center);
band_dBA = NaN(1,nBands);

for i = 1:nBands
    f1 = f_center(i) / (2^(1/6));   % lower band edge
    f2 = f_center(i) * (2^(1/6));   % upper band edge
    idx = find(f >= f1 & f <= f2);
    if isempty(idx)
        continue;
    end
    % integrate weighted pressure^2 in band
    pA_band_rms = sqrt(sum(pA_linear(idx)) * df);
    band_dBA(i) = 20*log10(pA_band_rms / p_ref);
end

%% --- Plot spectra ---
figure;
plot(f, SPL, 'b', 'LineWidth', 1.0); hold on;
plot(f, SPL_A, 'r', 'LineWidth', 1.0);
xlabel('Frequency (Hz)');
ylabel('SPL (dB re 20 \muPa)');
title(['SPL Spectrum (Total A-weighted = ', num2str(SPL_A_total,'%.2f'), ' dBA)']);
legend('Unweighted', 'A-weighted');
grid on; xlim([20 Fs/2]);

%% --- Plot 1/3-Octave Bands (A-weighted) ---
figure;
semilogx(f_center, band_dBA, 'ro-', 'LineWidth', 1.2, 'MarkerFaceColor', 'r');
grid on;
xlabel('Center Frequency (Hz)');
ylabel('Band Level (dBA)');
title('1/3-Octave A-weighted SPL');
xlim([20 20000]);
