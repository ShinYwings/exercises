## Install

1. mkdir build && cd build
2. cmake ..
3. make -j24
4. sudo make install
5. check python path is correct in setpath.sh
6. register in the systemctl in order to execute it automatically (Otherwise, you have to run setpath.sh every single shell)
    - reference : <https://ibks-platform.tistory.com/371>
7. type "mitsuba" in terminal (check your library is properly working)

## Run

1. make sure your mitsuba library has been installed. (See "/home/library/mitsuba/install_byshin.md")
2. make sure model, plane, data_list, and directory are correct
3. run make_xml.py (render_scene.py is in the make_xml.py)
4. Do same work in twice (train and test)
