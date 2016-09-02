from PyPWA.configurator import plugin_loader, templates
from PyPWA import libs

from PyPWA.libs import data, process, minimizers


def test_PluginLoading_ImportsPlugins_FindsAllLibs():
    """
    Ensures that the PluginLoader finds all the plugins when supplied
    with a module and nothing more.
    """
    loader = plugin_loader.PluginLoading(templates.OptionsTemplate)
    plugins = loader.fetch_plugin([libs])

    assert data.DataIterator in plugins
    assert data.DataParser in plugins
    assert process.Processing in plugins
    assert minimizers.MinuitOptions in plugins
    assert minimizers.MultiNestOptions in plugins

    assert len(plugins) == 5