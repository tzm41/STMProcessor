import dbaccess as dba
import dbupdate as dbu


def main():
    dba.displaySpectraNum()
    dba.getSpectrumFromID(4)
    dba.getSpectrumFromDoping('78K UD')
    dbu.insertGap(5, 0.261, 10)
    # dbu.insertSpectrum([2.12, 2.123, 5.643], [12.3, 1, 123], "78K UD")

if __name__ == "__main__":
    main()
