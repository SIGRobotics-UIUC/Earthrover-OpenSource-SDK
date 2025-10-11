from dataclasses import dataclass #we are using this because this is a data holder class (since its a config file) where its main operation is just to store data, very minimal edits

from ..config import TeleoperatorConfig #goes back one folder to import a base config file that defines how any teleoperator configuration should behave


@TeleoperatorConfig.register_subclass("earthrover_mini_plus") #this allows you to register a different teleoperator and allows you to differentiate various teleoperators
@dataclass #works with the import statement as a decorator so it knows for this class to auto create an __init__.py and other boilerplate code
class EarthroverMiniPlusConfig(TeleoperatorConfig):
    # the variables below don't have any default value so need to pass one in
    port: str #Port to connect to the earthrover
    ip: str #Robot's IP to connect to the earthrover
    
    #TODO: Come up later on with what other parameters we need for the config file