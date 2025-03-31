function [] = spectrogram_GUI()
%%%%% Graphical User Interface for Realtime Spectral Display
%
%  NOTE: requires audio toolbox
%
%  Mechanical Inputs
%  - internal microphone / sound card 

%  Outputs
%  - raw acoustic data
%  - time-frequency display
%
%  Copyright 2023 - Applied Physical Laboratory at University of Washington
%     written by David Dall'Osto
%%%%%

%Initialize Global Variables
samplerate = 4800;
aquisitiontime = 1/16; %time window (update rate)
R = complex(1);
fftl = samplerate*aquisitiontime;
win = hanning(fftl);
F = [0:fftl-1]/(fftl-1)*samplerate;
F(end/2+1:end)=[];
specdata = zeros(fftl/2,60);
psense1 = 20;
audio_card  = initializeSoundCard; %calls audioDeviceReader

%  Create and then hide the GUI as it is being constructed.
gui = figure('Visible','off','Position',[120,350,500,400]);
gui.Name = 'Microphone Aquisition and Analysis';
   % Move the GUI to the center of the screen.
movegui(gui,'center');
   % Make the GUI visible.
gui.Visible = 'on';

% Create plot axes     
   hplot_top = axes('Units','Normalized','Position',[.1 .65 .7 .3]);   
   plot([0:samplerate*aquisitiontime-1]/samplerate,[1:samplerate*aquisitiontime]*0,[0:samplerate*aquisitiontime-1]/samplerate,[1:samplerate*aquisitiontime]*0)
   title('pressure waveform')
   ylabel('Pa')
   ylim([-1 1]*2)

   hplot_bot = axes('Units','Normalized','Position',[.1 .15 .7 .3]);   
   imagesc([0:aquisitiontime.*size(specdata,2)],F,specdata)
   title('time-frequency display')

   ylabel('Hz')
   xlabel('seconds')
   cbar = colorbar;
   cbar.Position = [.9 .1 .025 .4];
   ylabel(cbar,'dB <uncalibrated>')
   caxis([-70 0])
   colormap jet
   axis xy
   
rec_on_off = 0; %initially, no record

%  Construct the GUI components.

% Create a red LED:
   hLED_REC=uicontrol('Style','pushbutton','Units','Normalized',...
            'Position',[.95 .8 .035 .1],...
            'Enable','off',...
            'Backgroundcolor','r'); 
% Create a record button
   hrecord = uicontrol('Style','pushbutton','String','ON','Units','Normalized',...
          'Position',[.825,.8,.1,.1],...
          'Callback',@(src,event)RECbutton_Callback(src,event,hLED_REC),'Fontsize',14);
   % htime = uicontrol('Style','text','String',datestr(now,'HH:MM:SS'),'Units','Normalized',...
   %        'Position',[.8725,.9,.1,.05],'Fontsize',12);
   % 
   hexit = uicontrol('Style','pushbutton','String','EXIT','Units','Normalized',...
          'Position',[.825,.65,.1,.1],...
          'Callback',@(src,event)EXITbutton_Callback(),'Fontsize',14);  

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%INTERNAL GUI FUNCTIONS   

%GUI RECORD BUTTON PRESS
function RECbutton_Callback(src,event,hLED_REC)
    
    rec_on_off = rec_on_off+hrecord.Value;
    if rem(rec_on_off,2)==1
        setup(audio_card)
    end

while rem(rec_on_off,2)==1
         % Now make the LED green
        set(hLED_REC,'Backgroundcolor','g');
        sampleSoundCard;
end

set(hLED_REC,'Backgroundcolor','r');
release(audio_card);

end

function EXITbutton_Callback()
release(audio_card);
close all
end

%FUNCTION TO INITIALIZE SOUND CARD
    function [s] = initializeSoundCard()

s = audioDeviceReader;
release(s);
s.SamplesPerFrame = aquisitiontime*samplerate;
s.SampleRate = samplerate;
end


    function sampleSoundCard
    [audioIn, nOverrun] = record(audio_card);
    if nOverrun~=0
        fprintf(['buffer overrun:   ' int2str(ceil(nOverrun/(aquisitiontime*samplerate)*100)) ' percent   --> increase aquisition time to allow for longer processing window \n'])
    end
    plot_data(audioIn);      
end

    function plot_data(audioIn)
  
         p1 = audioIn(:,1)*psense1;

         hplot_top.Children(1).YData = real(p1);

   pf = fft(win.*p1,fftl);
   pf(end/2+1:end)=[];
   Sf = pf.*conj(pf)./trapz(F,pf.*conj(pf)).*var(p1);
   
   specdata = circshift(specdata,1,2);
   specdata(:,1) = 10*log10(Sf);
   hplot_bot.Children.CData =  specdata;
   drawnow;
end

end  

