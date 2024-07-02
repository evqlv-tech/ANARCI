import shutil, os, subprocess
import site, sys
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop


class CustomInstallCommand(install):
    def run(self):
        super().run()
        self._post_install()

    @staticmethod
    def _post_install():
        # Post-installation routine
        ANARCI_LOC = os.path.join(
            site.getsitepackages()[0], "anarci"
        )  # site-packages/ folder
        ANARCI_BIN = sys.executable.split("python")[0]  # bin/ folder

        shutil.copy("bin/ANARCI", ANARCI_BIN)  # copy ANARCI executable
        print("INFO: ANARCI lives in: ", ANARCI_LOC)

        # stage muscle alignments for build
        # TODO: make this less hacky
        os.makedirs("build_pipeline/muscle_alignments", exist_ok=True)
        shutil.copy("all_js_aligned.fasta", "build_pipeline/muscle_alignments")

        # Build HMMs from IMGT germlines
        os.chdir("build_pipeline")
        print("INFO: Downloading germlines from IMGT and building HMMs...")
        print("INFO: running 'RUN_pipeline.sh', this will take a couple a minutes.")
        proc = subprocess.Popen(
            ["bash", "RUN_pipeline.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        o, e = proc.communicate()

        print(o.decode())
        print(e.decode())

        # Copy HMMs where ANARCI can find them
        shutil.copy("curated_alignments/germlines.py", ANARCI_LOC)
        os.mkdir(os.path.join(ANARCI_LOC, "dat"))
        shutil.copytree("HMMs", os.path.join(ANARCI_LOC, "dat/HMMs/"))

        # Remove data from HMMs generation
        try:
            shutil.rmtree("curated_alignments/")
            shutil.rmtree("muscle_alignments/")
            shutil.rmtree("HMMs/")
            shutil.rmtree("IMGT_sequence_files/")
        except OSError:
            pass


class CustomDevelopCommand(develop):
    def run(self):
        super().run()
        CustomInstallCommand._post_install()


setup(
    name="anarci",
    version="1.3",
    description="Antibody Numbering and Receptor ClassIfication",
    author="James Dunbar",
    author_email="opig@stats.ox.ac.uk",
    url="http://opig.stats.ox.ac.uk/webapps/ANARCI",
    packages=["anarci"],
    package_dir={"anarci": "lib/python/anarci"},
    data_files=[("bin", ["bin/muscle", "bin/muscle_macOS", "bin/ANARCI"])],
    include_package_data=True,
    scripts=["bin/ANARCI"],
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
    },
)
