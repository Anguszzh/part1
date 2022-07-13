import m5
from m5.objects import *
from caches import *

import argparse
parser = argparse.ArgumentParser(description=
                                'A simple system with 2-level cache.')
parser.add_argument("binary", default="",nargs="?",
                    type=str,help="Path to the binary to the execute.")
parser.add_argument("--l1i_size",
                    help=f"L1 instruction cache size. Default:16kB.")
parser.add_argument("--l1d_size",help=f"L1 data cache size. Default:64kB.")
parser.add_argument("--l2_size",help=f"L2 cache size. Default:256kB.")
options = parser.parse_args()

#create the system SimObject
system = System()

#set the clock on the system
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

#set up the timing mode for the memory simulation
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

#create a CPU
system.cpu = TimingSimpleCPU()

#create L1 caches
system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)

#connect the caches to the CPU ports
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

#create the system-wide memory bus
system.membus = SystemXBar()
"""
#connect the I-cache and D-cache ports directly to the membus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports
"""
#connect the L1 caches to the L2 bus
system.l2bus =L2XBar()

system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

#create L2 cache and connect it to the L2 bus and the memory bus
system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

#connect the PIO and interrupt ports to the memory bus, only for X86
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

#create a memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

binary = 'tests/test-progs/hello/bin/x86/linux/hello'

#for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation~")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'
        .format(m5.curTick(),exit_event.getCause()))