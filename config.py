config = {
    # Parameter counts
    "max_parameters_per_signature": 5,  # Max parameters per signature
    # Signature counts
    "min_signatures_per_interface": 1,  # Min signatures per interface
    "max_signatures_per_interface": 10,  # Max signatures per interface
    # Component settings
    "min_provided_interfaces_per_component": 1,  # Min provided interfaces per component
    "min_required_interfaces_per_component": 1,  # Min required interfaces per component
    # System settings
    "min_exposed_interfaces": 1,  # Min exposed interfaces in system
    "max_exposed_interfaces": 10,  # Max exposed interfaces in system
    # Allocation settings
    "min_allocation_groups": 1,  # Min allocation groups
    # Usage model settings
    "max_user_count": 20,  # Max users in closed workload
    "min_calls": 1,  # Min system calls in usage model
    "max_calls": 9,  # Max system calls in usage model
    # Value ranges
    "int_param_min": 0,  # Min value for integer parameters
    "int_param_max": 100,  # Max value for integer parameters
    "string_param_min_length": 5,  # Min length for string parameters
    "string_param_max_length": 150,  # Max length for string parameters
    "double_param_min": 0.0,  # Min value for double parameters
    "double_param_max": 100.0,  # Max value for double parameters
    "arrival_rate_min": 0.01,  # Min arrival rate for open workload
    "arrival_rate_max": 0.9,  # Max arrival rate for open workload
    "think_time_min": 0.5,  # Min think time for closed workload
    "think_time_max": 50.0,  # Max think time for closed workload
}
