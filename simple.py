import m5
from m5.objects import *

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

#create the system-wide memory bus
system.membus = SystemXBar()

#connect the I-cache and D-cache ports directly to the membus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

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