#eyJzdGF0ZSI6eyJidWlsZFByZXNldHMiOnsiZGVmYXVsdF9jb25maWciOnsibmFtZSI6ImRlZmF1bHRfY29uZmlnIiwiY29uZmlndXJhdGlvbiI6ImJhc2UiLCJkZWZpbml0aW9ucyI6W10sInJlbW92ZWRGbGFncyI6eyJDIjpbIi1PcyIsIi1mb21pdC1mcmFtZS1wb2ludGVyIl0sIkNYWCI6WyItT3MiLCItZm9taXQtZnJhbWUtcG9pbnRlciJdLCJBU00iOltdfSwiYWRkaXRpb25hbEZsYWdzIjp7IkMiOlsiLU8yIiwiLWZuby1vbWl0LWZyYW1lLXBvaW50ZXIiLCItZm5vLWlubGluZS1mdW5jdGlvbnMtY2FsbGVkLW9uY2UiLCItZnZhci10cmFja2luZy1hc3NpZ25tZW50cyJdLCJDWFgiOlsiLU8yIiwiLWZuby1vbWl0LWZyYW1lLXBvaW50ZXIiLCItZm5vLWlubGluZS1mdW5jdGlvbnMtY2FsbGVkLW9uY2UiLCItZnZhci10cmFja2luZy1hc3NpZ25tZW50cyJdLCJBU00iOltdfX19LCJjdXJyZW50Q29uZkluZGV4IjowfSwiZm9sZGVycyI6WyJ1c2VyIiwidXNlci90cCIsInVzZXIvd2l1cyIsInVzZXIvdHAvY29tbWFuZHMiXSwiZmlsZXMiOltdfQ==
include_directories(
	"../user"
	"../user/tp"
	"../user/wius"
	"../user/tp/commands"
)

target_sources(fw_v6 PRIVATE
	"../user/common.c"
	"../user/log.c"
	"../user/user.c"
	"../user/tp/tp.c"
	"../user/tp/tp_afe.c"
	"../user/tp/tp_buffer.c"
	"../user/tp/tp_command.c"
	"../user/tp/tp_fpga.c"
	"../user/tp/tp_mux.c"
	"../user/tp/tp_power.c"
	"../user/tp/tp_tx.c"
	"../user/wius/wius_gpio.c"
	"../user/wius/wius_power.c"
	"../user/wius/wius_spi.c"
	"../user/wius/wius_tcp.c"
	"../user/wius/wius_udp.c"
	"../user/wius/wius_wifi.c"
	"../user/tp/commands/tp_command_ctrlpwr.c"
	"../user/tp/commands/tp_command_delayns.c"
	"../user/tp/commands/tp_command_enreplies.c"
	"../user/tp/commands/tp_command_ping.c"
	"../user/tp/commands/tp_command_setpowersave.c"
	"../user/tp/commands/tp_command_sleepms.c"
	"../user/tp/commands/tp_command_swmux.c"
	"../user/tp/commands/tp_command_triggershot.c"
	"../user/tp/commands/tp_command_writeafe.c"
	"../user/tp/commands/tp_command_writefpga.c"
	"../user/tp/commands/tp_command_writespi.c"
	"../user/tp/commands/tp_command_writetx.c"
	"../user/tp/tp.c"
	"../user/tp/tp_afe.c"
	"../user/tp/tp_buffer.c"
	"../user/tp/tp_command.c"
	"../user/tp/tp_fpga.c"
	"../user/tp/tp_mux.c"
	"../user/tp/tp_power.c"
	"../user/tp/tp_tx.c"
	"../user/tp/commands/tp_command_ctrlpwr.c"
	"../user/tp/commands/tp_command_delayns.c"
	"../user/tp/commands/tp_command_enreplies.c"
	"../user/tp/commands/tp_command_ping.c"
	"../user/tp/commands/tp_command_setpowersave.c"
	"../user/tp/commands/tp_command_sleepms.c"
	"../user/tp/commands/tp_command_swmux.c"
	"../user/tp/commands/tp_command_triggershot.c"
	"../user/tp/commands/tp_command_writeafe.c"
	"../user/tp/commands/tp_command_writefpga.c"
	"../user/tp/commands/tp_command_writespi.c"
	"../user/tp/commands/tp_command_writetx.c"
	"../user/wius/wius_gpio.c"
	"../user/wius/wius_power.c"
	"../user/wius/wius_spi.c"
	"../user/wius/wius_tcp.c"
	"../user/wius/wius_udp.c"
	"../user/wius/wius_wifi.c"
	"../user/tp/commands/tp_command_ctrlpwr.c"
	"../user/tp/commands/tp_command_delayns.c"
	"../user/tp/commands/tp_command_enreplies.c"
	"../user/tp/commands/tp_command_ping.c"
	"../user/tp/commands/tp_command_setpowersave.c"
	"../user/tp/commands/tp_command_sleepms.c"
	"../user/tp/commands/tp_command_swmux.c"
	"../user/tp/commands/tp_command_triggershot.c"
	"../user/tp/commands/tp_command_writeafe.c"
	"../user/tp/commands/tp_command_writefpga.c"
	"../user/tp/commands/tp_command_writespi.c"
	"../user/tp/commands/tp_command_writetx.c"
)

get_target_property(interface_compile_options slc INTERFACE_COMPILE_OPTIONS)
	list(REMOVE_ITEM interface_compile_options $<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:C>>:-Os>)
	list(REMOVE_ITEM interface_compile_options $<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:C>>:-fomit-frame-pointer>)
	list(REMOVE_ITEM interface_compile_options $<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:CXX>>:-Os>)
	list(REMOVE_ITEM interface_compile_options $<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:CXX>>:-fomit-frame-pointer>)
set_target_properties(fw_v6 PROPERTIES INTERFACE_COMPILE_OPTIONS "${interface_compile_opitions}")

target_compile_options(fw_v6 PRIVATE
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:C>>:-O2>
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:C>>:-fno-omit-frame-pointer>
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:C>>:-fno-inline-functions-called-once>
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:C>>:-fvar-tracking-assignments>
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:CXX>>:-O2>
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:CXX>>:-fno-omit-frame-pointer>
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:CXX>>:-fno-inline-functions-called-once>
	$<$<AND:$<CONFIG:default_config>,$<COMPILE_LANGUAGE:CXX>>:-fvar-tracking-assignments>
)
