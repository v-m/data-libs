from setuptools import setup, find_packages

setup(
    name="revlibs-logger",
    version="0.2.0",
    author="Demeter Sztanko",
    author_email="demeter.sztanko@revolut.com",
    packages=find_packages(),
    package_data={"logger": ["logging.yaml"]},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "pyaml>=18.11.0",
        "google-cloud-logging>=1.10.0",
        "slacker-log-handler>=1.7.1",
    ],
    namespace_packages=["revlibs"],
)
