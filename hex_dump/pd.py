

import sigrokdecode as srd

class SamplerateError(Exception):
    pass

class Decoder(srd.Decoder):
    api_version = 3
    id = 'hex_dump'
    name = 'Hex Dump'
    longname = 'Hex Dump'
    desc = 'Convert digital signal to hex values.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = []
    tags = ['Clock/timing', 'Util']
    channels = (
        {'id': 'data', 'name': 'Data', 'desc': 'Data line'},
    )
    options = (
        {'id': 'baudrate', 'desc': 'Baud rate', 'default': 1000},
    )
    annotations = (
        ('hex', 'hex val'),
    )

    n_bits_read = 0
    read_byte = 0

    def putx(self, data):
        self.put(self.first_bit_in_byte, self.samplenum, self.out_ann, data)

    def __init__(self):
        self.reset()

    def reset(self):
        self.ss_last_bit = None
        self.first_bit_in_byte = None
        self.n_bits_read = 0
        self.read_byte = 0
        self.first_reading = True
        self.print_byte = False
        self.start_sample = None

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def metadata(self, key, value):
        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def updateReadByte(self, val):
        self.read_byte = (self.read_byte << 1) | val
        if self.n_bits_read >= 8:
            self.n_bits_read = 0
            self.print_byte = True

    def print_read_byte(self):
        self.putx([0, ['%02X' % self.read_byte]])
        self.read_byte = 0
        # next byte starts from next sample
        self.first_bit_in_byte = self.samplenum
        self.print_byte = False
        

    def decode(self):
        if not self.samplerate:
            raise SamplerateError('Cannot decode without samplerate.')

        baudrate = self.options['baudrate']

        if self.samplerate % baudrate:
            raise SamplerateError('Sample rate shall be a multiple of the Baud rate.')
            
        # Get the first edge on the data line.
        val = self.wait({0: 'e'})[0]
        self.start_sample = self.samplenum
        self.ss_last_bit = self.samplenum
        self.first_bit_in_byte = self.samplenum

        
        # get the peiod of the signal
        time_per_bit = 1.0 / float(baudrate)
        samples_per_bit = int(self.samplerate * time_per_bit)
        samples_per_halfbit = int(samples_per_bit / 2)

        self.first_reading = True
        self.print_byte = False

        i = 0

        while True:
            val = self.wait({'skip': samples_per_halfbit})[0]

            signal_sample = self.samplenum - self.start_sample


            # use sample between the edges of the signal, where the signal is stable
            if not (signal_sample + samples_per_halfbit) % samples_per_bit:
                self.n_bits_read = self.n_bits_read + 1
                self.updateReadByte(val)
                self.ss_last_bit = self.samplenum

            # print the byte corresponding to the sampled octect, align it to th signal edges
            if not signal_sample % samples_per_bit and self.print_byte:
                self.print_read_byte()

