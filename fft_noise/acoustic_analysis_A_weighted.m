
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

% Apply A-weighting to spectral levels
SPL_A = SPL + A_weight;

%% --- Compute overall A-weighted level (single value) ---
% Convert spectral levels back to linear pressure, apply weighting, integrate
df = Fs/Nfft;                    % frequency resolution
pA_linear = (Prms .* 10.^(A_weight/20)).^2;  % weighted pressure^2
pA_total_rms = sqrt(sum(pA_linear) * df);    % integrate over band
SPL_A_total = 20*log10(pA_total_rms / p_ref);

fprintf('Overall A-weighted SPL = %.2f dBA\n', SPL_A_total);

%% --- Plot results ---
figure;
plot(f, SPL, 'b', 'LineWidth', 1.0); hold on;
plot(f, SPL_A, 'r', 'LineWidth', 1.0);
xlabel('Frequency (Hz)');
ylabel('SPL (dB re 20 \muPa)');
title(['Sound Pressure Level Spectrum (A-weighted total = ', ...
       num2str(SPL_A_total,'%.2f'), ' dBA)']);
legend('Unweighted', 'A-weighted');
grid on;
xlim([20 Fs/2]);
