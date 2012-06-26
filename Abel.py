import math
import SpotlightDialog
import SpotlightGui

defaultFilterSelection = 1
defaultSmoothingFactor = 5.0
defaultDeltaSpacing = 0.2579 # physical spacing between points of p(l) (pixels)
defaultWavelength = 0.634e-3    #  units: mm
defaultSRI = 0.2595  # soot refractive index (imaginary part) - called E in eq.

defaultAverageOption = 0
defaultBackgroundSelection = 0
defaultReferenceImage = ''
defaultBackgroundLeft = 0
defaultBackgroundRight = 0

##----------------------------------

class AbelTransform:
    def __init__(self, parentAoi):
        self.parentAoi = parentAoi
        params = {'name': 'AbelTransform',
                  'filter': defaultFilterSelection,
                  'smoothingFactor': defaultSmoothingFactor,
                  'deltaSpacing': defaultDeltaSpacing,
                  'wavelength': defaultWavelength,
                  'sri': defaultSRI,
                  'averageOption': defaultAverageOption,
                  'backgroundSelection': defaultBackgroundSelection,
                  'referenceImage': defaultReferenceImage,
                  'backgroundLeft': defaultBackgroundLeft,
                  'backgroundRight': defaultBackgroundRight}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        if params.has_key('filter'):
            global defaultFilterSelection
            defaultFilterSelection = params['filter']
        if params.has_key('smoothingFactor'):
            global defaultSmoothingFactor
            defaultSmoothingFactor = params['smoothingFactor']
        if params.has_key('deltaSpacing'):
            global defaultDeltaSpacing
            defaultDeltaSpacing = params['deltaSpacing']
        if params.has_key('wavelength'):
            global defaultWavelength
            defaultWavelength = params['wavelength']
        if params.has_key('sri'):
            global defaultSRI
            defaultSRI = params['sri']
        if params.has_key('averageOption'):
            global defaultAverageOption
            defaultAverageOption = params['averageOption']
        if params.has_key('backgroundSelection'):
            global defaultBackgroundSelection
            defaultBackgroundSelection = params['backgroundSelection']
        if params.has_key('referenceImage'):
            global defaultReferenceImage
            defaultReferenceImage = params['referenceImage']
        if params.has_key('backgroundLeft'):
            global defaultBackgroundLeft
            defaultBackgroundLeft = params['backgroundLeft']
        if params.has_key('backgroundRight'):
            global defaultBackgroundRight
            defaultBackgroundRight = params['backgroundRight']

        self.params = {'name': 'AbelTransform',
                       'filter': defaultFilterSelection,
                       'smoothingFactor': defaultSmoothingFactor,
                       'deltaSpacing': defaultDeltaSpacing,
                       'wavelength': defaultWavelength,
                       'sri': defaultSRI,
                       'averageOption': defaultAverageOption,
                       'backgroundSelection': defaultBackgroundSelection,
                       'referenceImage': defaultReferenceImage,
                       'backgroundLeft': defaultBackgroundLeft,
                       'backgroundRight': defaultBackgroundRight}

    def calcSootVolumeFraction(self, lineprofile, refLineProfile, fromImageFlag):
        'convert Abel transform distribution to soot volume fraction'
        distr = self.AbelSVF(lineprofile, refLineProfile, fromImageFlag)
        params = self.getParams()
        wavelength = params['wavelength']    #  units: mm
        E = params['sri']
        const = wavelength / (6.0 * math.pi * E)
        params = self.getParams()
        delta = params['deltaSpacing']
        svf = []
        for x in range (0, len(distr)):
            f = const * distr[x] / delta
            svf.append(f)
        return svf

    def calcIntensity(self, lineprofile):
        'divide by delta (delta L)'
        distr = self.AbelIntensity(lineprofile)
        params = self.getParams()
        delta = params['deltaSpacing']
        out = []
        for x in range (0, len(distr)):
            f = distr[x] / delta
            out.append(f)
        return out

    def AbelSVF(self, lineprofile, refLineProfile, fromImageFlag):
        """Calculate Abel Transform. """
        if len(lineprofile) < 5:
            return []

        params = self.getParams()
        filter = params['filter']
        smoothingFactor = params['smoothingFactor']
        backgroundLeft = params['backgroundLeft']
        backgroundRight = params['backgroundRight']
        backgroundSelection = params['backgroundSelection']

        # Note: splitProfile() function includes the centerpoint for both
        # left and right sides.
        left, right = self.splitProfile(lineprofile)
        leftRef, rightRef = self.splitProfile(refLineProfile)

        if left == [] or right == []:
            m = 'Internal Error in AbelSVF - left or right are null'
            self.parentAoi.showMessage(m)
            return []

        if backgroundSelection != 0:
            if leftRef == [] or rightRef == []:
                m = 'Internal Error in AbelSVF - leftRef or rightRef are null'
                self.parentAoi.showMessage(m)
                return []
            if len(left) != len(leftRef):
                m = 'Internal Error in AbelSVF - error: left  not same as leftRef'
                self.parentAoi.showMessage(m)
                return []

        # calculate the Abel transform distribution based on SVF
        if params['averageOption'] == 0:
            if backgroundSelection == 0:
                """Average left and right profiles and then divide by average
                background value. For background average I'm using leftRef
                which was generated in the Aoi class from backgroundLeft and
                backgroundRight values."""
                av = self.doAverage(left, right)
                div = self.doDivide(av, leftRef) # leftRef is av backgrnd value
                distr = self.doAbel(div, filter, smoothingFactor)
                return self.remapDistribution(distr)
            else:
                """Divide left by leftRef and right by rightRef and then average
                those results together. The profile comes from reference image"""
                divLeft = self.doDivide(left, leftRef)
                divRight = self.doDivide(right, rightRef)
                div = self.doAverage(divLeft, divRight)
                distr = self.doAbel(div, filter, smoothingFactor)
                return self.remapDistribution(distr)
        else:
            """Calculate distribution separately for left and right. The
            reference profiles (leftRef and rightRef) was either calculated
            from the background constants or was obtained from the reference
            image. Either way the refProfile was generated in the Aoi class."""
            divLeft = self.doDivide(left, leftRef)
            divRight = self.doDivide(right, rightRef)
            distrleft = self.doAbel(divLeft, filter, smoothingFactor)
            distrright = self.doAbel(divRight, filter, smoothingFactor)
            return self.remapDistribution(distrleft, distrright)

    def AbelIntensity(self, lineprofile):
        if len(lineprofile) < 5:
            return []

        params = self.getParams()
        filter = params['filter']
        smoothingFactor = params['smoothingFactor']

        # Note: splitProfile() function includes the centerpoint for both
        # left and right sides.
        left, right = self.splitProfile(lineprofile)
        if left == [] or right == []:
            m = 'Internal Error in AbelIntensity - left or right are null'
            self.parentAoi.showMessage(m)
            return []
        if len(left) != len(right):
            m = 'Internal Error in AbelIntensity - left not same length as right'
            self.parentAoi.showMessage(m)
            return []

        # calculate the Abel transform distribution
        if params['averageOption'] == 0:
            av = self.doAverage(left, right)
            distr = self.fabeltran(av, filter, smoothingFactor)
            return self.remapDistribution(distr)
        else:
            # do left side
            distrleft = self.fabeltran(left, filter, smoothingFactor)
            # do right side
            distrright = self.fabeltran(right, filter, smoothingFactor)
            return self.remapDistribution(distrleft, distrright)

    def AbelTestFromFile(self, el, proj):
        'perform Abel transform - data from Zeng-guang in.dat file'
        params = self.getParams()
        filter = params['filter']
        smoothingFactor = params['smoothingFactor']
        distr = self.fabeltran(proj, filter, smoothingFactor)
        deltaal = el[1]-el[0]
        for i in range(len(distr)):
            distr[i] = distr[i]/deltaal
        return distr

    def doAbel(self, div, filter, smoothingFactor):
        'take natural log and the Abel'
        log = self.naturalLog(div)
        return self.fabeltran(log, filter, smoothingFactor)

    def doAverage(self, left, right):
        'returns a list thats an average of the two lists sent in'
        if len(left) != len(right):
            m = 'Internal Error in doAverage - left  not same as right'
            self.parentAoi.showMessage(m)
            return []

        av = []
        for i in range (len(right)):
            av.append((left[i] + right[i]) / 2)
        return av

    def getAsList(self, number, listlength):
        'returns a list of identical values'
        out = []
        for i in range(listlength):
            out.append(number)
        return out

    def combineProfiles(self, left, right):
        """
        Combines two lists into one. Note that the number of points in the
        resultant list will be one less than the sum of the two that went in.
        This is because the rirst element from left and right array are
        combined (averaged) to make a centerpoint. This way it will undue
        the duplication of the centerpoint done in splitProfile() function.
        """
        out = []
        # copy left array to out array skipping the first element
        for i in range (len(left)-1):
            out.append(left[i+1])
        out.reverse()

        # generate the centerpoint
        m1 = left[0]
        m2 = right[0]
        out.append((m1+m2)/2)

        # add the right side
        for i in range (len(right)-1):
            out.append(right[i+1])
        return out

    def remapDistribution(self, left, right=[]):
        'generate a full distribution of left side and right'
        if right:
            'combine the separately generated left and right'
            return self.combineProfiles(left, right)
        else:
            """now generate both sides just from one side"""
            bothsides = []
            for i in range (len(left)):   # includes centerpoint
                bothsides.append(left[i])
            bothsides.reverse()
            for i in range (len(left)-1): # excludes centerpoint the second time
                bothsides.append(left[i+1])
            return bothsides

    def doDivide(self, pixels, refPixels):
        """returs a division of ref-image line by the flame-image line.
        This is the (Io/Is) - needed for Soot Volume Fraction.
        flame image is (Is) and ref image is (Io) (background).
        """
        out = []
        for i in range (len(pixels)):
            # pixel of soot must be lower than background
            p = min(pixels[i], refPixels[i]-0.00001)
            if p == 0.0:
                p = 0.000005
            out.append(refPixels[i]/p)
        return out

    def naturalLog(self, pixels):
        'returns a ln(pixels)'
        out = []
        for i in range (len(pixels)):
            p = max(0.00001, pixels[i])    # cut out neg numbers and zero
            p = math.log(p)
            m = max(0.00001, p)    # cut out neg numbers and zero
            out.append(m)
        return out

    def splitProfile(self, lineprofile):
        """Splits a profile line into a left and right half. The number
        of elements in the profile is always odd. The way Zeng-guang wants
        it done is that both left and right include the centerpoint. For
        example, if profile is 9 pixels long, then left and right both will
        be 5 pixels long. """

        if len(lineprofile) == 0:  # is 0 when there is no reference image
            return ([],[])
        linelength = len(lineprofile)
        half = linelength / 2        # take half
        right = lineprofile[half:]   # slice out the right side (include center)
        left = lineprofile[:half+1]  # slice out the left side (include center)
        left.reverse()               # reverse order

        if len(left) == 0:  # is 0 when there is no reference image
            return ([],[])
        elif len(left) != len(right): # must have been odd - try subt 1
            newRight = right[1:]      # skip 0th element of right
            if len(left) == len(newRight):
                return (left, newRight)
            else:  # still no good - get out
                m = 'Internal Error in splitProfile - left does not equal right'
                self.parentAoi.showMessage(m)
                return ([],[])
        else:
            return (left, right)

    def fabeltran(self, p, fm, smthf):
        """Starting date 5/25/95, Last update, 6/29/98 (Zeng-guang Yuan)
    fabeltran convers the projection of an axisymmetric special
    distribution back to the distribution using the Abel transform with
    user specified filters on the projection. The characteristic wave
    number for the filter, smthf, is the total wave number in the
    entire al domain of the projection p(l).
    Argument list:
    p[] - 1-D input float projection array
    f[] - 1-D output float projection array
    pf_size - integer gives the size of the array p[] and f[]
    fm - a filter identification number
    smthf - float, between 1 and pf_size/2, determining the characteristic
            frequency (wave number) of the filter. The larger the number
            the higher the cut-off frequency.
    Note:
    a) The results form this function should be divided by
    delta l or delta r in the calling function to get the right value of
    the special distribution.
    b) delta r is equal to delta l. Theoretically,the two do not have to
    be identical, but practically it is easier this way. The current code
    requires this.
    c) normally f_size should be equal to p_size. It is possible to make
    f_size different from p_size. If f_size > p_size, then some zero of
    p[] is forced. If f_size < p_size, you cann't recover p[] from f[].
    This program uses pf_size for both.
    d) since p[] is assumed to be zero for l > p_size. The size of f[] can
    be anything greater than p_size. In that case, p_size is automatically
    extended to f_size.
    e) the function getgee() has to be an even function.
    Written by Zeng-guang Yuan
    Modified by Bob Klimek 2/8/01"""

        pf_size = len(p)
        if fm == 0:
            distr = self.abeltrans(p)
            return distr
        elif fm == 1:
            # Low-pass filter selected
            omigan = 2.0 * math.pi * smthf / float(pf_size-1)
        elif fm == 2 or fm == 3:
            # Smooth by a rectangular window selected
            omigan = smthf
        else:
            print 'Unknown filter selected'

        # Loop through each lambda point for mker[]
        mker = []
        for j in range(pf_size):
            f = []
            distr = []
            for k in range(pf_size):
                f.append(self.getgee(k+j,omigan,fm) + self.getgee(k-j,omigan,fm))

            distr = self.abeltrans(f)

            # Passing transform results to mker.
            # mker is a pf_size * pf_size 1-D array
            for i in range(pf_size):
                mker.append(distr[i])

            SpotlightGui.gui.Yield() # --allows setting cursor to hourglass
            #SpotlightDialog.Yield() # --allows setting cursor to hourglass

        # simpson for f
        f = []
        coef = 1.0/3.0  # 0.33333333...
        for i in range(pf_size):
            if self.odd(pf_size):
                me = (pf_size-5)/2
                # mker counter is this:  c = y * aoiWidth + x
                mker1 = mker[pf_size-2 * pf_size + i]
                mker2 = mker[pf_size-1 * pf_size + i]
                last = coef * (4.0 * p[pf_size-2] * mker1 + p[pf_size-1] * mker2)
            else:
                me = (pf_size-4)/2
                last = coef*4.0*p[pf_size-1]*mker[pf_size-1 * pf_size + i]

            f.append(coef * p[0] * mker[i] + last) # mker[i][0] in c program

            # This is a bit confusing because what's normally thought of as "x" and "y"
            # as in (c=y*w+x) or f[x][y] is switched here. The x is normally in the
            # inner loop but here it is the outer loop.
            for m in range(me+1):
                x = i
                y = 2*m+1
                c = y * pf_size + x
                mker1 = mker[c]
                x = i
                y = 2*m+2
                c = y * pf_size + x
                mker2 = mker[c]
                f[i] = f[i] + coef*2.0*(2.0*p[2*m+1]*mker1 + p[2*m+2]*mker2)

        distr = []
        for i in range(pf_size):
            distr.append(f[i])

        return distr

    def getgee(self, l, omigan, fm):
        """The getgee() returns the value of gee for the three given
        arguments. The gee function must be even. """

        fl = float(l)
        if fl < 0.0:
            fl = -fl

        gee = 0.0
        if fm == 1:
            if fl == 0.0:
                gee = omigan/math.pi
            else:
                #gee = math.sin(omigan*fl) / fl / math.pi
                gee = math.sin(omigan*fl) / (fl * math.pi)
        elif fm == 2:
            if fl <= omigan:
                gee = 1.0
            if fl == omigan + 1:
                gee = 0.5
            gee = gee/(2*omigan + 2.0)
        elif fm == 3:
            if fl <= omigan:
                gee = 1.0
            if fl == omigan + 1:
                gee = 0.75
            if fl == omigan + 2:
                gee = 0.50
            if fl == omigan + 3:
                gee = 0.25
            gee = gee/(2*omigan + 4.0)
        else:
            print 'unknown filter'

        return gee

    def abeltrans(self, p):
        """Last update, Oct. 9, '95 (Zeng-guang Yuan)
    the last change is to add the last term for Simpson's rule.

    abeltrans convers the projection of an axisymmetric special
    distribution back to the distribution with the Abel transform.
    Array p[] is the projection and is passed in and pout is the output
    spatial distribution. The integer argument p_size gives the size of
    p[] array. The results form this function should be divided by
    delta l or delta r in the calling function to get the right value of
    the special distribution. Written by Zeng-guang Yuan

    An open type numerical integration (three-point Steffensen's formulas)
    is used to avoid the singularity of the integrand at r = l. The formula
    needs four consecutive data points. Simpson rules is used for the rest
    of the integration. The given data of p[] is extended by patching zeros
    to infinity. An analytical derivation is used to extend the calculation
    to infinit  make sure the application of open type integration to the
    last given point."""

        p_size = len(p)
        pout = []
        for j in range(p_size):

            # The numerical integration of Abel transform in this code
            # is divided into three parts: Steffensen's formula, Simpson rule
            # and an analytical result

            # Three-point Steffensen's formula
            fj = float(j)

            fsubs = 2.0 * fj + 1.0
            pj1 = -2.666666667 * (j+1)/(fsubs * math.sqrt(fsubs))
            fsubs = fj + 1.0
            pj2 = 0.16666666667 * (j+2)/(fsubs * math.sqrt(fsubs))
            fsubs = 2.0 * fj + 3.0
            pj3 = -0.513200239 * (j+3)/(fsubs * math.sqrt(fsubs))
            pj4 = pj1 + pj2 + pj3

            if j > p_size-2:	  # j = p_size-1
              fsum = -p[j] * pj4
            elif j > p_size-3:    # j = p_size-2
              fsum = p[j+1]*pj1 - p[j]*pj4
            elif j > p_size-4:    # j= p_size-3
              fsum = p[j+1]*pj1 + p[j+2]*pj2 - p[j]*pj4
            else:		  # j= p_size-4 and less
              fsum = p[j+1]*pj1 + p[j+2]*pj2 + p[j+3]*pj3 - p[j]*pj4

            # If the integration points are more than four, Simpson's rule (SR) is
            # applied. Since the calculation is extended to infinity, The last term
            # of Simpson's rule is always a patched zero and therefore neglected.
            if j < p_size-4:
                if self.odd(p_size):  # the highest sum. index for SR
                    p_idx = p_size-1
                    k = -1
                else:
                    p_idx = p_size
                    k = 1

                p_idx2 = p_idx/2      # half of p_idx

                if self.odd(j):     # an intermediate parameter for sum. limit
                    jup = j + k
                else:
                    jup = j

                sum_idx_e = p_idx2-jup/2-2  # up. lim. of the 2nd sum. in SR
                sum_idx_o = sum_idx_e-1     # up. lim. of the 3rd sum. in SR

                # now determine the last term, k is temperary
                k = p_size - j

                if self.odd(k):
                    n_last = p_size - 1
                else:
                    n_last = 0

                # now calculate each term
                fsubs = fj + 2.0
                simp1 = -0.014731391 * p[j+4] * (j+4) / (fsubs * math.sqrt(fsubs))

                simp2 = 0.0
                for k in range(1, sum_idx_e + 1):
                    fsubs = (k + 1.5) * (fj + k + 1.5)
                    simp2 = simp2 + (j+2*k+3)*p[j+2*k+3]/(fsubs*math.sqrt(fsubs))

                simp2 = -0.1666666667 * simp2

                simp3 = 0.0
                for k in range(1, sum_idx_o + 1):
                    fsubs = (k + 2.0) * (fj+k+2.0)
                    simp3 = simp3 + (j+2*k+4)*p[j+2*k+4]/(fsubs*math.sqrt(fsubs))

                simp3 = -0.0833333333*simp3

                fsum = fsum + simp1 + simp2 + simp3

                # Last term add or not?
                if n_last != 0:
                    fsubs = float(n_last*n_last - fj*fj)
                    fsum = fsum - 0.33333*p[p_size-1]*n_last/(fsubs*math.sqrt(fsubs))

            # The last term is from analytical derivation extending the domain to infinity
            fsum = fsum + 0.3535339*p[j]/math.sqrt(fj + 2.0)
            pout.append(fsum/math.pi) # spatial distribution

        return pout

    def odd(self, a):
        'odd(a) = 1 for odd a, 0 for even a'
        if a % 2:
            return 1
        else:
            return 0

    def getZengGuangsTestData(self):
        'returns two columns of numbers (same as Zeng-guangs in.dat format)'
        d = []
        d.append((0.0,  3.0))
        d.append((0.2,  2.99973332))
        d.append((0.4,  2.99893314))
        d.append((0.6,  2.99759904))
        d.append((0.8,  2.99573029))
        d.append((1.0,  2.99332591))
        d.append((1.2,  2.99038459))
        d.append((1.4,  2.98690475))
        d.append((1.6,  2.98288451))
        d.append((1.8,  2.97832168))
        d.append((2.0,  2.97321375))
        d.append((2.2,  2.96755792))
        d.append((2.4,  2.96135104))
        d.append((2.6,  2.95458965))
        d.append((2.8,  2.94726992))
        d.append((3.0,  2.93938769))
        d.append((3.2,  2.93093842))
        d.append((3.4,  2.92191718))
        d.append((3.6,  2.91231866))
        d.append((3.8,  2.90213714))
        d.append((4.0,  2.89136646))
        d.append((4.2,  2.88))
        d.append((4.4,  2.86803068))
        d.append((4.6,  2.85545093))
        d.append((4.8,  2.84225263))
        d.append((5.0,  2.82842712))
        d.append((5.2,  2.81396517))
        d.append((5.4,  2.79885691))
        d.append((5.6,  2.78309181))
        d.append((5.8,  2.76665863))
        d.append((6.0,  2.74954542))
        d.append((6.2,  2.73173937))
        d.append((6.4,  2.71322686))
        d.append((6.6,  2.69399332))
        d.append((6.8,  2.67402319))
        d.append((7.0,  2.65329983))
        d.append((7.2,  2.63180546))
        d.append((7.4,  2.60952103))
        d.append((7.6,  2.58642611))
        d.append((7.8,  2.56249878))
        d.append((8.0,  2.53771551))
        d.append((8.2,  2.51205095))
        d.append((8.4,  2.48547782))
        d.append((8.6,  2.45796664))
        d.append((8.8,  2.42948554))
        d.append((9.0,  2.4))
        d.append((9.2,  2.36947252))
        d.append((9.4,  2.33786227))
        d.append((9.6,  2.30512473))
        d.append((9.8,  2.27121113))
        d.append((10.0,  2.23606798))
        d.append((10.2,  2.19963633))
        d.append((10.4,  2.16185106))
        d.append((10.6,	2.12263987))
        d.append((10.8,	2.08192219))
        d.append((11.0,	2.03960781))
        d.append((11.2,  1.99559515))
        d.append((11.4,  1.94976922))
        d.append((11.6,	1.90199895))
        d.append((11.8,	1.8521339))
        d.append((12.0,  1.8))
        d.append((12.2,  1.74539394))
        d.append((12.4,  1.68807583))
        d.append((12.6,  1.6277592))
        d.append((12.8,  1.56409718))
        d.append((13.0,  1.49666295))
        d.append((13.2,  1.42492105))
        d.append((13.4,  1.34818396))
        d.append((13.6,  1.26554336))
        d.append((13.8,  1.17575508))
        d.append((14.0,  1.07703296))
        d.append((14.2,  0.966643678))
        d.append((14.4,  0.84))
        d.append((14.6,  0.688186021))
        d.append((14.8,  0.488262225))
        d.append((15.0,  0.000000158))
        d.append((15.2,	0.0))
        d.append((15.4,	0.0))
        d.append((15.6,	0.0))
        d.append((15.8,	0.0))
        d.append((16.0,	0.0))
        d.append((16.2,	0.0))
        d.append((16.4,	0.0))
        d.append((16.6,	0.0))
        d.append((16.8,	0.0))
        d.append((17.0,	0.0))
        d.append((17.2,	0.0))
        d.append((17.4,	0.0))
        d.append((17.6,	0.0))
        d.append((17.8,	0.0))
        d.append((18.0,	0.0))
        d.append((18.2,	0.0))
        d.append((18.4,	0.0))
        d.append((18.6,	0.0))
        d.append((18.8,	0.0))
        d.append((19.0,	0.0))
        d.append((19.2,	0.0))
        d.append((19.4,	0.0))
        d.append((19.6,	0.0))
        d.append((19.8,	0.0))
        # put it in another format
        el = []
        proj = []
        for n in d:
            x, y = n
            el.append(x)
            proj.append(y)
        return (el, proj)
