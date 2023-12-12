#!/bin/sh
tmux new-session -d -s  s500_session 'python3 ./DataAcqSoftware/start_ping_set_params_data_acq_table_input_nmea_out.py'
#tmux new-session  s500_session 'python3 ./DataAcqSoftware/start_ping_set_params_data_acq_table_input_nmea_out.py &';  # start new detached tmux session, run htop 
tmux split-window;                             		# split the detached tmux session
tmux send 'python3 ./DataAcqSoftware/nmea_logger.py &' ENTER;       
#tmux send 'ls &' ENTER;             	 		# send 2nd command  to 2nd pane. 
 tmux a #;
