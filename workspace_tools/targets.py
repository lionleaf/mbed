"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

CORE_LABELS = {
    "ARM7TDMI-S": "ARM7",
    "Cortex-M0" : "M0",
    "Cortex-M0+": "M0P",
    "Cortex-M3" : "M3",
    "Cortex-M4" : "M4",
    "Cortex-M4F" : "M4"
}

import os
import shutil


class Target:
    def __init__(self):
        # ARM Core
        self.core = None

        # Is the disk provided by the interface chip of this board virtual?
        self.is_disk_virtual = False

        # list of toolchains that are supported by the mbed SDK for this target
        self.supported_toolchains = None

        # list of extra specific labels
        self.extra_labels = []

        # list of macros (-D)
        self.macros = []

        # Default online compiler:
        self.default_toolchain = "ARM"

        self.name = self.__class__.__name__

    def program_cycle_s(self):
        return 4 if self.is_disk_virtual else 1.5

    def get_labels(self):
        return [self.name, CORE_LABELS[self.core]] + self.extra_labels

    def init_hooks(self, hook, toolchain_name):
        pass


class LPC2368(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "ARM7TDMI-S"
        self.extra_labels = ['NXP', 'LPC23XX']
        self.supported_toolchains = ["ARM", "GCC_ARM", "GCC_CR"]


class LPC1768(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['NXP', 'LPC176X', 'MBED_LPC1768']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM", "GCC_CS", "GCC_CR", "IAR"]


class LPC11U24(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11UXX', 'LPC11U24_401']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]
        self.default_toolchain = "uARM"


class LPC11U24_301(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11UXX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]


class KL05Z(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0+"
        self.extra_labels = ['Freescale', 'KLXX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO"]
        self.is_disk_virtual = True


class KL25Z(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0+"
        self.extra_labels = ['Freescale', 'KLXX']
        self.supported_toolchains = ["ARM", "GCC_CW_EWL", "GCC_CW_NEWLIB", "GCC_ARM"]
        self.supported_form_factors = ["ARDUINO"]
        self.is_disk_virtual = True


class KL46Z(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0+"
        self.extra_labels = ['Freescale', 'KLXX']
        self.supported_toolchains = ["GCC_ARM", "ARM"]
        self.supported_form_factors = ["ARDUINO"]
        self.is_disk_virtual = True


class K20D50M(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4"
        self.extra_labels = ['Freescale']
        self.supported_toolchains = ["GCC_ARM", "ARM"]
        self.is_disk_virtual = True


class K64F(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['Freescale', 'KPSDK_MCUS', 'KPSDK_CODE', 'FRDM']
        self.macros = ["CPU_MK64FN1M0VMD12", "FSL_RTOS_MBED"]
        self.supported_toolchains = ["ARM", "GCC_ARM"]
        self.supported_form_factors = ["ARDUINO"]
        self.is_disk_virtual = True
        self.default_toolchain = "ARM"


class LPC812(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0+"
        self.extra_labels = ['NXP', 'LPC81X']
        self.supported_toolchains = ["uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO"]
        self.is_disk_virtual = True


class LPC810(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0+"
        self.extra_labels = ['NXP', 'LPC81X']
        self.supported_toolchains = ["uARM"]
        self.default_toolchain = "uARM"
        self.is_disk_virtual = True


class LPC4088(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['NXP', 'LPC408X']
        self.supported_toolchains = ["ARM", "GCC_CR", "GCC_ARM"]
        self.is_disk_virtual = True

    def init_hooks(self, hook, toolchain_name):
        if toolchain_name in ['ARM_STD', 'ARM_MICRO']:
            hook.hook_add_binary("post", self.binary_hook)

    @staticmethod
    def binary_hook(t_self, resources, elf, binf):
        if not os.path.isdir(binf):
            # Regular binary file, nothing to do
            return
        outbin = open(binf + ".temp", "wb")
        partf = open(os.path.join(binf, "ER_IROM1"), "rb")
        # Pad the fist part (internal flash) with 0xFF to 512k
        data = partf.read()
        outbin.write(data)
        outbin.write('\xFF' * (512*1024 - len(data)))
        partf.close()
        # Read and append the second part (external flash) in chunks of fixed size
        chunksize = 128 * 1024
        partf = open(os.path.join(binf, "ER_IROM2"), "rb")
        while True:
            data = partf.read(chunksize)
            outbin.write(data)
            if len(data) < chunksize:
                break
        partf.close()
        outbin.close()
        # Remove the directory with the binary parts and rename the temporary
        # file to 'binf'
        shutil.rmtree(binf, True)
        os.rename(binf + '.temp', binf)
        t_self.debug("Generated custom binary file (internal flash + SPIFI)")


class LPC4330_M4(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['NXP', 'LPC43XX']
        self.supported_toolchains = ["ARM", "GCC_CR", "IAR", "GCC_ARM"]


class LPC4330_M0(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC43XX']
        self.supported_toolchains = ["ARM", "GCC_CR", "IAR"]


class LPC1800(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['NXP', 'LPC43XX']
        self.supported_toolchains = ["ARM", "GCC_CR", "IAR"]


class STM32F407(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['STM', 'STM32F4XX']
        self.supported_toolchains = ["ARM", "GCC_ARM"]


class NUCLEO_F030R8(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['STM', 'STM32F0', 'STM32F030R8']
        self.supported_toolchains = ["ARM", "uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_F072RB(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['STM', 'STM32F0', 'STM32F072RB']
        self.supported_toolchains = ["ARM", "uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_F103RB(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['STM', 'STM32F1', 'STM32F103RB']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_F302R8(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['STM', 'STM32F3', 'STM32F302R8']
        self.supported_toolchains = ["ARM", "uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_F334R8(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['STM', 'STM32F3', 'STM32F334R8']
        self.supported_toolchains = ["ARM", "uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_F401RE(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['STM', 'STM32F4', 'STM32F401RE']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_F411RE(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4"
        self.extra_labels = ['STM', 'STM32F4', 'STM32F411RE']
        self.supported_toolchains = ["ARM", "uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_L053R8(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0+"
        self.extra_labels = ['STM', 'STM32L0', 'STM32L053R8']
        self.supported_toolchains = ["ARM", "uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class NUCLEO_L152RE(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['STM', 'STM32L1', 'STM32L152RE']
        self.supported_toolchains = ["ARM", "uARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO", "MORPHO"]


class STM32F3XX(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4"
        self.extra_labels = ['STM', 'STM32F3XX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]
        self.default_toolchain = "uARM"


class LPC1347(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['NXP', 'LPC13XX']
        self.supported_toolchains = ["ARM", "GCC_ARM"]


class LPC1114(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11XX_11CXX', 'LPC11XX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM", "GCC_CR"]
        self.default_toolchain = "uARM"


class LPC11C24(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11XX_11CXX', 'LPC11CXX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]


class LPC11U35_401(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11UXX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM", "GCC_CR"]
        self.default_toolchain = "uARM"


class LPC11U35_501(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11UXX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM", "GCC_CR"]
        self.default_toolchain = "uARM"


class LPC11U37_501(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11UXX']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM", "GCC_CR"]
        self.default_toolchain = "uARM"


class UBLOX_C027(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['NXP', 'LPC176X']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM", "GCC_CS", "GCC_CR", "IAR"]
        self.macros = ['TARGET_LPC1768']
        self.supported_form_factors = ["ARDUINO"]


class NRF51822(Target):
    # the following is a list of possible Nordic softdevices in decreasing order
    # of preference.
    EXPECTED_SOFTDEVICES_WITH_OFFSETS = [
        {
            'name' : 's110_nrf51822_7.0.0_softdevice.hex',
            'offset' : 0x16000
        },
        {
            'name' : 's110_nrf51822_6.0.0_softdevice.hex',
            'offset' : 0x14000
        }
    ]
    OUTPUT_EXT = '.hex'

    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ["NORDIC", "NRF51822_MKIT"]
        self.supported_toolchains = ["ARM", "GCC_ARM"]
        self.is_disk_virtual = True

    def program_cycle_s(self):
        return 6

    def init_hooks(self, hook, toolchain_name):
        if toolchain_name in ['ARM_STD', 'ARM_MICRO']:
            hook.hook_add_binary("post", self.binary_hook)

    @staticmethod
    def binary_hook(t_self, resources, elf, binf):
        for hexf in resources.hex_files:
            found = False
            for softdeviceAndOffsetEntry in NRF51822.EXPECTED_SOFTDEVICES_WITH_OFFSETS:
                if hexf.find(softdeviceAndOffsetEntry['name']) != -1:
                    found = True
                    break
            if found:
                break
        else:
            t_self.debug("Hex file not found. Aborting.")
            return

        # Merge user code with softdevice
        t_self.debug("Patching Hex file %s" % softdeviceAndOffsetEntry['name'])
        from intelhex import IntelHex
        binh = IntelHex()
        binh.loadbin(binf, offset=softdeviceAndOffsetEntry['offset'])

        sdh = IntelHex(hexf)
        sdh.merge(binh)

        with open(binf.replace(".bin", ".hex"), "w") as f:
            sdh.tofile(f, format='hex')


class LPC1549(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['NXP', 'LPC15XX']
        self.supported_toolchains = ["uARM", "GCC_CR"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO"]


class LPC11U68(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0+"
        self.extra_labels = ['NXP', 'LPC11U6X']
        self.supported_toolchains = ["uARM", "GCC_CR", "GCC_ARM"]
        self.default_toolchain = "uARM"
        self.supported_form_factors = ["ARDUINO"]


class DISCO_F100RB(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['STM', 'STM32F1', 'STM32F100RB']
        self.supported_toolchains = ["GCC_ARM"]
        self.default_toolchain = "uARM"


class DISCO_F051R8(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['STM', 'STM32F0', 'STM32F051', 'STM32F051R8']
        self.supported_toolchains = ["GCC_ARM"]
        self.default_toolchain = "uARM"


class DISCO_F407VG(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['STM', 'STM32F4', 'STM32F407', 'STM32F407VG']
        self.supported_toolchains = ["GCC_ARM"]
        self.default_toolchain = "uARM"


class DISCO_F303VC(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['STM', 'STM32F3', 'STM32F303', 'STM32F303VC']
        self.supported_toolchains = ["GCC_ARM"]
        self.default_toolchain = "uARM"


class XADOW_M0(LPC11U35_501):
    def __init__(self):
        LPC11U35_501.__init__(self)
        self.extra_labels = ['NXP', 'LPC11UXX', 'LPC11U35_501']
        self.macros = ['TARGET_LPC11U35_501']


class ARCH_BLE(NRF51822):
    def __init__(self):
        NRF51822.__init__(self)
        self.extra_labels = ['NORDIC', 'NRF51822']
        self.macros = ['TARGET_NRF51822']


class ARCH_PRO(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M3"
        self.extra_labels = ['NXP', 'LPC176X']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM", "GCC_CS", "GCC_CR", "IAR"]
        self.macros = ['TARGET_LPC1768']
        self.supported_form_factors = ["ARDUINO"]


class ARCH_GPRS(LPC11U37_501):
    def __init__(self):
        LPC11U37_501.__init__(self)


class LPCCAPPUCCINO(LPC11U37_501):
    def __init__(self):
        LPC11U37_501.__init__(self)


class HRM1017(NRF51822):
    def __init__(self):
        NRF51822.__init__(self)
        self.extra_labels = ['NORDIC', 'NRF51822']
        self.macros = ['TARGET_NRF51822']


class ARM_MPS2(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.macros = ['CMSDK_CM4']
        self.supported_toolchains = ["ARM", "GCC_ARM"]
        self.default_toolchain = "ARM"


class RBLAB_NRF51822(NRF51822):
    def __init__(self):
        NRF51822.__init__(self)
        self.extra_labels = ['NORDIC', 'NRF51822']
        self.macros = ['TARGET_NRF51822']
        

class GHI_MBUINO(LPC11U24):
    def __init__(self):
        LPC11U24.__init__(self)
        self.core = "Cortex-M0"
        self.extra_labels = ['NXP', 'LPC11UXX']
        self.macros = ['TARGET_LPC11U24']
        self.supported_toolchains = ["ARM", "uARM", "GCC_ARM"]
        self.default_toolchain = "uARM"
        
class MTS_GAMBIT(Target):
    def __init__(self):
        Target.__init__(self)
        self.core = "Cortex-M4F"
        self.extra_labels = ['Freescale', 'KPSDK_MCUS', 'KPSDK_CODE', 'K64F']
        self.supported_toolchains = ["ARM", "GCC_ARM"]
        self.macros = ['TARGET_K64F', "CPU_MK64FN1M0VMD12", "FSL_RTOS_MBED"]
        self.is_disk_virtual = True
        self.default_toolchain = "ARM"

# Get a single instance for each target
TARGETS = [
    LPC2368(),
    LPC1768(),
    LPC11U24(),
    LPC11U24_301(),
    KL05Z(),
    KL25Z(),
    KL46Z(),
    K20D50M(),
    K64F(),
    LPC812(),
    LPC810(),
    LPC4088(),
    LPC4330_M4(),
    STM32F3XX(),
    STM32F407(),
    NUCLEO_F030R8(),
    NUCLEO_F072RB(),
    NUCLEO_F103RB(),
    NUCLEO_F302R8(),
    NUCLEO_F334R8(),
    NUCLEO_F401RE(),
    NUCLEO_F411RE(),
    NUCLEO_L053R8(),
    NUCLEO_L152RE(),
    LPC1347(),
    LPC1114(),
    LPC11C24(),
    LPC11U35_401(),
    LPC11U35_501(),
    NRF51822(),
    UBLOX_C027(),
    LPC1549(),
    LPC11U68(),
    DISCO_F051R8(),
    DISCO_F100RB(),
    DISCO_F303VC(),
    DISCO_F407VG(),
    XADOW_M0(),
    ARCH_BLE(),
    ARCH_PRO(),
    ARCH_GPRS(),
    LPCCAPPUCCINO(),
    HRM1017(),
    ARM_MPS2(),
    RBLAB_NRF51822(),
    GHI_MBUINO(),
    MTS_GAMBIT(),
]

# Map each target name to its unique instance
TARGET_MAP = {}
for t in TARGETS:
    TARGET_MAP[t.name] = t

TARGET_NAMES = TARGET_MAP.keys()

# Some targets with different name have the same exporters
EXPORT_MAP = {}
