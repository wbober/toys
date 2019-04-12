#!/bin/bash

# vmware-toy is a simple set of functions which wrap vmware vmrun utility
# an and allow for running applications inside guest.
#
# This can be used, for example, to:
# a) open Office documents inside guest by clicking on them in host (vm_cmd_open_share)
# b) run apps inside guest using a command line on host (vm_cmd_start)

VMRUN="vmrun -T player"
SECRET_TOOL_KEY="service vmware-toy"

_secret_tool_lookup()
{
    echo $(secret-tool search ${SECRET_TOOL_KEY} 2>&1 | awk -F' = ' " \$1 == \"${1}\" { print \$2 }")
}

_vm_get_credentials()
{
    local USER=$(_secret_tool_lookup attribute.user)
    local PASS=$(_secret_tool_lookup secret)
    
    if [ -z $(which secret-tool) ]; then
        echo "secret-tool not found"
        return 1
    fi
    
    if [ -z ${USER} ] || [ -z ${PASS} ]; then
        echo "User credentials not found."
        echo "Please use secret-tool --label='vmware-toy' service vmware-toy \
              user <USER-NAME> \
              vmx <PATH-TO-VMX \
              share <PATH-TO-VMX-SHARE>"
        return 1
    fi

    echo "-gu ${USER} -gp ${PASS}"
}

_vm_run()
{
    local VMX=$(_secret_tool_lookup attribute.vmx)
    CMD=$1
    shift 1

    ${VMRUN} $(_vm_get_credentials) ${CMD} ${VMX} "$@"
}

_vm_caffeine()
{
    local PROGRAM="C:\Windows\caffeine.exe"
    _vm_run runProgramInGuest -interactive -activeWindow "$PROGRAM" "$@"
}

vm_cmd_start()
{
    local PROGRAM="C:\Windows\System32\cmd.exe"
    _vm_run runProgramInGuest -interactive -activeWindow "$PROGRAM" "/c start ${1}"
}

vm_cmd_open_share()
{
    local SHARE=$(_secret_tool_lookup attribute.share)
    vm_cmd_start "\"\" \"${SHARE}\\$(realpath "${1}")\""
}

# Attach to gnome screen saver and toggle Coffeine application in guest 
# accordingly. This allows for updating presence status in IM application.
caffeine_attach()
{
    (
        dbus-monitor --session "type='signal',interface='org.gnome.ScreenSaver'" |
        while read x; do
            case "$x" in 
            *"boolean true"*) _vm_caffeine "-appoff";;
            *"boolean false"*) _vm_caffeine "-appon";;
            esac
        done
    ) &
}