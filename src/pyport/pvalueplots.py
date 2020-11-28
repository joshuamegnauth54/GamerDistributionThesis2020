import matplotlib.pyplot as plt
import seaborn as sns

def p_value_plots(observed, replicates, labels):
    p_values = [sim_pair for sim_pair in zip(observed, replicates)]