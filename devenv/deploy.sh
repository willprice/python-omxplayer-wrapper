#!/usr/bin/env bash
cd "$(dirname "$(realpath $0)")"

ANSIBLE_PLAYBOOK="${ANSIBLE_PLAYBOOK:-ansible-playbook}"

"$ANSIBLE_PLAYBOOK" --inventory-file=inventory/raspberrypis \
                    --ask-become-pass \
                    site.yml
