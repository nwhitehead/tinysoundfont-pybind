project('tinysoundfont', 'cpp', version: '0.2.2' )

py = import('python').find_installation()

pybind11_config = find_program('pybind11-config')
pybind11_config_ret = run_command(pybind11_config, ['--includes'], check: true)
pybind11 = declare_dependency(
    include_directories: [pybind11_config_ret.stdout().split('-I')[-1].strip()],
)

py.extension_module(
    'tinysoundfont',
    'src/main.cpp',
    dependencies: [pybind11],
    install: true
)
