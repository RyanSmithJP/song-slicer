import wave as wv
import numpy as np
import plotly.graph_objects as go
import json
from scipy.signal import resample

def generate_waveform_with_slider(sanitized_song_name):
    print("Starting waveform generation...")
    vocals_file = f"/app/src/static/{sanitized_song_name}"
    print(f"Processing file: {vocals_file}")

    # Open the audio file
    try:
        song = wv.open(vocals_file, 'rb')
        freq = song.getframerate()  # Original sampling frequency
        samples = song.getnframes()  # Number of original samples
        t = samples / freq  # Duration in seconds
        signal = np.frombuffer(song.readframes(samples), dtype=np.int16)
        song.close()
        print(f"Audio file loaded successfully: {samples} samples, {freq} Hz, {t:.2f} seconds.")
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None

    # Downsample for faster rendering if necessary
    print("Starting downsampling...")
    max_points = 2000
    step = max(1, len(signal) // max_points)
    signal = signal[::step]  # Reduce the number of samples
    samples = len(signal)
    print(f"Downsampling complete: {samples} samples, original duration: {t:.2f} seconds.")

    # Create traces and slider steps
    print("Generating traces and slider steps...")
    traces = []
    sliders_steps = []

    for sample_rate in range(1, 6):  # Sample rates from 1 to 5
        print(f"Generating trace for sample rate {sample_rate}...")
        resampled_signal = resample(signal, int(samples * sample_rate))
        resampled_samples = len(resampled_signal)
        
        # Use the original duration `t` for the time axis
        time_axis = np.linspace(0, t, num=resampled_samples)

        # Create a trace for each sample rate
        traces.append(
            go.Scatter(
                x=time_axis,
                y=resampled_signal,
                visible=(sample_rate == 1),  # Show only the first trace initially
                name=f"Rate {sample_rate}",
            )
        )

        # Define the slider step
        sliders_steps.append({
            "args": [{"visible": [i == (sample_rate - 1) for i in range(5)]}],
            "label": str(sample_rate),
            "method": "update",
        })

        print(f"Trace for sample rate {sample_rate} generated with {resampled_samples} samples.")

    print("Traces and slider steps generated.")

    # Create layout with a slider
    print("Creating layout with slider...")
    layout = go.Layout(
        title="Waveform with Sample Rate Slider",
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        sliders=[{
            "active": 0,
            "currentvalue": {"prefix": "Sample Rate: "},
            "steps": sliders_steps,
        }]
    )

    # Generate figure
    print("Generating final figure...")
    fig = go.Figure(data=traces, layout=layout)
    fig_json = json.loads(fig.to_json())
    print("Waveform generation complete. JSON output below:")
    print(json.dumps(fig_json, indent=2))  # Print the JSON for debugging

    return fig_json
