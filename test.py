# The goal: record audio with this script

import wave         # read/write waveform audio (WAV)
import pyaudio      # used to record the audio
import asyncio      # used for concourent asynchronic code
import json         # handles json files
import io           # provides a consistant interface for wroking with input/output
import os           # the way to interact with the operating system for vaios reasons
import threading    # careate and manage threads withing the process

# Now that we have the right libraries, we can go ahead and write the code that will
# aventually record the audio toa WAV file.

# Set enviroment variable for ALSA - Advances Linux Sound Architecture
os.environ['PA_ALSA_PLUGHW'] = '1'   # tells ALSA to use audio card 0 (my mic)

# Load configuration from a JSON file - for now it's only for the recording part
def load_config():
    #dir_path = os.path.dirname(os.path.abspath(__file__))
    #config_path = os.path.join(dir_path, 'config.json')
    with open('./config.json', 'r') as config_file:
        return json.load(config_file)
    
# Set config using the funcion:
config = load_config()

# List audio devices - for later use
def list_audio_devices():
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []
    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_device_index(0, i)
        devices.append((i, device_info['name'], device_info['maxInputChannels']))
    audio.terminate()
    return devices

# Selects input device using the list created above
def select_input_device():
    devices = list_audio_devices()
    if not devices:
        print("No audio devices found.")
        return None
    suitable_devices = [i for i, name, channels in devices if channels >= config['audio']['channels']]
    if suitable_cevices:
        return suitable_devices[0]
    else:
        print("No suitable input devices found with  the required number of channels.")
        print("Available devices:")
        for i, name, channels in devices:
            print(f"Devices {i}: {name}, channels: {channels}")
        return None

def validate_device_channels(device_index, required_channels):
    audio = pyaudio.PyAudio()
    device_info = audio.get_device_info_by_index(device_index)
    audio.terminate()
    return device_info['maxInputChannels'] >= required_channels

# And now for the purpose of this script - audio recording
def record_audio():
    form_1 = getattr(pyaudio, config['audio']['format'])
    chans = config['audio']['channels']
    samp_rate = config['audio']['sample_rate']
    chunk = config['audio']['chunk_size']
    record_secs = config['audio']['record_seconds']
    dev_index = config['audio']['device_index']

    if dev_index is None or not validate_device_channels(dev_index, chans):
        dev_index = select_input_device()
        if dev_index is None:
            return None

    #script_dir = os.path.dirname(os.abspath(__file__))
    wav_output_filename = os.path.join('./', 'shazam.wav')

    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                                    input_device_index=dev_index, input=True,
                                    frames_per_buffer=chunk)
    except OSError as e:
        print(f"Error opening audio stream: {e}")
        return None

    frames = []

    try:
        for _ in range(int((samp_rate / chunk) * record_secs)):
            data = stream.read(chunk)
            frames.append(data)
    except IOError as e:
        print(f"Error recording audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    wavefile = wave.open(wav_output_filename, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    return wav_output_filename

if __name__ == "__main__":
    recorded_file = record_audio()
    if recorded_file:
        print(f"Successfully recorded to {recorded_file}")
    else:
        print("Recording failed.")
