import os
import matplotlib.pyplot as plt


def configure_matplotlib_defaults(mpl_config_dir: str = "./.matplotlib") -> None:
    """Configures Matplotlib configuration directory and CJK font fallbacks."""
    os.environ["MPLCONFIGDIR"] = mpl_config_dir
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [
        "Hiragino Sans",
        "Hiragino Maru Gothic Pro",
        "AppleGothic",
        "Arial Unicode MS",
        "sans-serif",
    ]
