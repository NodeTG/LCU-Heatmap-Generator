import pymeow


def read_offsets(proc, base_address, offsets):
    basepoint = pymeow.read_int64(proc, base_address)

    current_pointer = basepoint

    for i in offsets[:-1]:
        current_pointer = pymeow.read_int64(proc, current_pointer+i)
    
    return current_pointer + offsets[-1]


def reload_addrs():
    global proc, pos_base_addr, rot_base_addr, x_addr, z_addr, rot_addr, city_addr #, y_addr

    try:
        proc = pymeow.process_by_name("LEGOLCUR_DX11.exe")
    except Exception as e:
        print(f"Failed to get process handle; {e}")
        return

    pos_base_addr = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C77C78
    rot_base_addr = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C74920
    city_addr = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x17F86A0

    x_addr = read_offsets(proc, pos_base_addr, [0x90])
#    y_addr = read_offsets(proc, pos_base_addr, [0x94])
    z_addr = read_offsets(proc, pos_base_addr, [0x98])
    rot_addr = read_offsets(proc, rot_base_addr, [0x218])


def read_positions():
    return [pymeow.read_float(proc, x_addr), pymeow.read_float(proc, z_addr)]


def read_rotation():
    return pymeow.read_float(proc, rot_addr)


def check_city_loaded():
    return pymeow.read_bool(proc, city_addr)


try:
    proc = pymeow.process_by_name("LEGOLCUR_DX11.exe")
    reload_addrs()
except Exception as e:
    print(f"Failed to get process handle; {e}")
