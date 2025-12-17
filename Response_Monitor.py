import time

class ResponseMonitor:
    """
    Monitor respons sinyal terhadap step input.

    Atribut:
      name           : nama sinyal (string)
      target         : nilai target akhir (default 0)
      tol            : toleransi untuk settling time (fraction, default 0.02)
      times, values  : list waktu dan nilai yang tercatat
      rise_time      : waktu mencapai kriteria rise
      settling_time  : waktu masuk dan bertahan dalam tol
      overshoot      : persentase overshoot
    """
    def __init__(self, name, target=0, tol=0.02):
        self.name = name
        self.target = target
        self.tol = tol
        self.start_time = None
        self.times = []
        self.values = []
        self.rise_time = None
        self.settling_time = None
        self.overshoot = None
        self.settled = False

    def update(self, value):
        now = time.time()
        if self.start_time is None:
            self.start_time = now
        t = now - self.start_time
        self.times.append(t)
        self.values.append(value)

        # Rise time: pertama kali value mendekati target (10% step)
        step = abs(self.target) if self.target else max(abs(v) for v in self.values)
        if self.rise_time is None and abs(value - self.target) <= 0.1 * step:
            self.rise_time = t

        # Overshoot: dihitung berdasarkan peak
        peak = max(self.values, key=lambda v: abs(v - self.target))
        if self.overshoot is None:
            self.overshoot = ((abs(peak - self.target) - abs(self.target or peak))
                              / (abs(self.target) if self.target else abs(peak))) * 100

        # Settling time: bertahan dalam ±tol*target (atau ±tol*peak) selama window terakhir
        if not self.settled:
            ref = abs(self.target) if self.target else abs(peak)
            tol_range = self.tol * ref
            if abs(value - self.target) <= tol_range:
                window = 5
                if len(self.values) >= window and all(abs(v - self.target) <= tol_range
                                                      for v in self.values[-window:]):
                    self.settling_time = t
                    self.settled = True

    def summary(self):
        print(f"--- {self.name.upper()} RESPONSE METRICS ---")
        print(f"Rise time     : {self.rise_time:.3f} s" if self.rise_time is not None else "Rise time     : N/A")
        print(f"Settling time : {self.settling_time:.3f} s" if self.settling_time is not None else "Settling time : N/A")
        print(f"Overshoot     : {self.overshoot:.2f} %" if self.overshoot is not None else "Overshoot     : N/A")
        if self.times:
            print(f"Duration      : {self.times[-1]:.2f} s")

class TrackingResponse:
    """
    Monitor waktu respons tracking hingga objek ke tengah.

    Atribut:
      name           : nama (e.g. 'h_offset')
      tol            : toleransi proximity ke pusat (fraction)
      start_time     : waktu deteksi pertama
      response_time  : waktu dari deteksi hingga dalam tol
      done           : flag selesai
    """
    def __init__(self, name, tol=0.05):
        self.name = name
        self.tol = tol
        self.start_time = None
        self.response_time = None
        self.done = False

    def update(self, value):
        now = time.time()
        # rekam deteksi pertama
        if self.start_time is None:
            self.start_time = now
        # jika belum selesai, cek proximity
        if not self.done and abs(value) <= self.tol:
            self.response_time = now - self.start_time
            self.done = True

    def summary(self):
        print(f"--- {self.name.upper()} TRACKING RESPONSE ---")
        if self.response_time is not None:
            print(f"Response time : {self.response_time:.3f} s (tol ±{self.tol})")
        else:
            print(f"Response time : N/A (objek belum mencapai tol ±{self.tol})")
