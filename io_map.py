# io_map.py
# Central config for all pins (outputs and inputs) with type and address
# You can assign any name you want to each channel for clarity.
# Example: 'hx460a', 'hx460b', 'main_valve', etc.

PINS = {
    # Outputs (coils)
    "output1": {"type": "coil", "address": 0},
    "output2": {"type": "coil", "address": 1},
    "output3": {"type": "coil", "address": 2},
    "output4": {"type": "coil", "address": 3},
    "output5": {"type": "coil", "address": 4},
    "output6": {"type": "coil", "address": 5},
    "output7": {"type": "coil", "address": 6},
    "output8": {"type": "coil", "address": 7},

    # Inputs (discrete inputs)
    "hx460a": {"type": "discrete_input", "address": 0},  # input9
    "hx460b": {"type": "discrete_input", "address": 1},  # input10
    "input1": {"type": "discrete_input", "address": 2},
    "input2": {"type": "discrete_input", "address": 3},
    "input3": {"type": "discrete_input", "address": 4},
    "input4": {"type": "discrete_input", "address": 5},
    "input15": {"type": "discrete_input", "address": 6},
    "input16": {"type": "discrete_input", "address": 7},
    "input17": {"type": "discrete_input", "address": 8},
    "input18": {"type": "discrete_input", "address": 9},
    "input19": {"type": "discrete_input", "address": 10},
    "input20": {"type": "discrete_input", "address": 11},
    "input21": {"type": "discrete_input", "address": 12},
    "input22": {"type": "discrete_input", "address": 13},
    "input23": {"type": "discrete_input", "address": 14},
    "input24": {"type": "discrete_input", "address": 15},
}

# To add or rename pins, just edit the keys and addresses above.
# Example: PINS["emergency_stop"] = {"type": "discrete_input", "address": 2}
