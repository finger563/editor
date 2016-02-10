from PyQt4 import QtCore
from collections import OrderedDict
import hashlib
import json
import uuid
import inspect

class BaseClass(QtCore.QObject):
    def __init__(self):
        self.uuid = None

    def get_kind(self):
        return self.__class__.__name__        

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_uuid(self):
        if self.uuid == None:
            self.set_uuid(str(uuid.uuid4()))
        return self.uuid

class Parameter(BaseClass):
    def __init__(self, name, value, unit = None, allowed = []):
        self.kind = type(value)
        self.name = name
        if (allowed == [] or value in allowed):
            self.value = value
        else:
            print "ERROR:: Value not Legal"
        self.unit = unit
        self.allowed = allowed

class Model(BaseClass):
    def __init__(self, parameters):
        BaseClass.__init__(self)
        self.children = []
        self.parameters = []
        for parameter in parameters:
            self.add_parameter(parameter)

    def get_parameters(self):
        return self.parameters

    def get_parameter(self, name):
        return [a for a in self.parameters if a.name == name][0]

    def add_parameter(self, new_parameter):
        self.parameters.append(new_parameter)

def ModelFactory(metamodel, base_class=Model):
    def __init__(self, **kwargs):
        parameters = []
        for key, value in kwargs.items():
            if key not in [a.name for a in metamodel.fields]:
                raise TypeError("Argument %s not valid for %s" 
                    % (key, self.__class__.__name__))
            argument = [a for a in metamodel.fields if a.name == key]
            if argument != []:
                parameters.append(Parameter(name=key, value=value, allowed=argument[0].allowed))
        for field in metamodel.fields:
            if field.name not in [p.name for p in parameters]:
                parameters.append(Parameter(name=field.name, value=field.default,
                                            allowed=field.allowed))
        base_class.__init__(self, parameters)
    newclass = type(metamodel.name, (base_class,),{"__init__": __init__})
    return newclass

class MetaModelField(BaseClass):
    def __init__(self, name, kind, default, allowed, validator=None):
        self.name = name
        self.kind = kind
        self.default = default
        self.allowed = allowed
        self.validator = validator

class MetaModel(BaseClass):
    def __init__(self, name, uuid = "", fields = []):
        self.name = name
        self.uuid = uuid
        self.fields = fields
    def add_field(field):
        self.fields.append(field)

class MetaContainment(BaseClass):
    def __init__(self, uuid = "", parent = "", child = "", cardinality = ""):
        self.uuid = uuid
        self.parent = parent
        self.child = child
        self.cardinality = cardinality

class MetaPointer(BaseClass):
    def __init__(self, name = "", uuid="", src = "", dst = ""):
        self.name = name
        self.uuid = uuid
        self.src = src
        self.dst = dst
        
# MetaModel Dictionary
meta_dictionary = OrderedDict()

# Save Function
def save(obj = None):
    global meta_dictionary
    if obj != None:
        if str(type(obj)) == "<class '__main__.MetaModel'>":
            sub_dictionary = OrderedDict()
            sub_dictionary["fields"] = []
            for field in obj.fields:
                sub_dictionary["fields"].append(vars(field))
            sub_dictionary["name"] = obj.name
            sub_dictionary["uuid"] = obj.uuid
            sub_dictionary["kind"] = "MetaModel"
            meta_dictionary[obj.uuid] = sub_dictionary
        elif str(type(obj)) == "<class '__main__.MetaContainment'>":
            sub_dictionary = OrderedDict()
            sub_dictionary["fields"] = [{"parent" : obj.parent,
                                         "child" : obj.child,
                                         "cardinality" : obj.cardinality}]
            sub_dictionary["uuid"] = obj.uuid
            sub_dictionary["kind"] = "MetaContainment"            
            meta_dictionary[obj.uuid] = sub_dictionary
        elif str(type(obj)) == "<class '__main__.MetaPointer'>":
            sub_dictionary = OrderedDict()
            sub_dictionary["fields"] = [{"src" : obj.src,
                                         "dst" : obj.dst}]
            sub_dictionary["uuid"] = obj.uuid
            sub_dictionary["name"] = obj.name
            sub_dictionary["kind"] = "MetaPointer"            
            meta_dictionary[obj.uuid] = sub_dictionary            
    return meta_dictionary

# MetaModel Classes in ROSMOD
meta_project = MetaModel("Project",
                         str(uuid.uuid4()),
                         [MetaModelField("name", "string", "NewProject", [])])
meta_software = MetaModel("Software",
                          str(uuid.uuid4()),
                          [MetaModelField("name", "string", "NewSoftware", [])])
meta_package = MetaModel("Package",
                         str(uuid.uuid4()),
                         [MetaModelField("name", "string", "NewPackage", [])])
meta_component = MetaModel("Component",
                           str(uuid.uuid4()),
                         [MetaModelField("name", "string", "NewComponent", []),
                          MetaModelField("component_type", "string", "base", ["base",
                                                                              "ksp",
                                                                              "sumo"])])
meta_message = MetaModel("Message",
                         str(uuid.uuid4()),
                         [MetaModelField("name", "string", "NewMessage", []),
                          MetaModelField("definition", "string", "", [])])
meta_service = MetaModel("Service",
                         str(uuid.uuid4()),
                         [MetaModelField("name", "string", "NewService", []),
                          MetaModelField("definition", "string", "", [])])
meta_client = MetaModel("Client",
                        str(uuid.uuid4()),
                        [MetaModelField("name", "string", "NewClient", [])])
meta_server = MetaModel("Server",
                        str(uuid.uuid4()),
                        [MetaModelField("name", "string", "NewServer", []),
                         MetaModelField("priority", "integer", 0, []),
                         MetaModelField("deadline", "float", 0.0, [])])
meta_publisher = MetaModel("Publisher",
                           str(uuid.uuid4()),
                           [MetaModelField("name", "string", "NewPublisher", [])])
meta_subscriber = MetaModel("Subscriber",
                            str(uuid.uuid4()),
                            [MetaModelField("name", "string", "NewSubscriber", []),
                             MetaModelField("priority", "integer", 0, []),
                             MetaModelField("deadline", "float", 0.0, [])])
meta_timer = MetaModel("Timer",
                       str(uuid.uuid4()),
                       [MetaModelField("name", "string", "NewTimer", []),
                        MetaModelField("period", "float", 0.0, []),
                        MetaModelField("priority", "integer", 0, []),
                        MetaModelField("deadline", "float", 0.0, [])])

meta_hardware = MetaModel("Hardware",
                          str(uuid.uuid4()),
                          [MetaModelField("name", "string", "NewHardware", [])])
meta_host = MetaModel("Host",
                      str(uuid.uuid4()),
                      [MetaModelField("name", "string", "NewHost", []),
                       MetaModelField("ip_address", "string", "NewHost", []),
                       MetaModelField("username", "string", "NewHost", []),
                       MetaModelField("sshkey", "string", "NewHost", []),
                       MetaModelField("deployment_path", "string", "NewHost", []),
                       MetaModelField("install_path", "string", "NewHost", []),
                       MetaModelField("architecture", "string", "NewHost", [])])

meta_deployment = MetaModel("Deployment",
                            str(uuid.uuid4()),
                            [MetaModelField("name", "string", "NewDeployment", [])])
meta_node = MetaModel("Node",
                      str(uuid.uuid4()),
                      [MetaModelField("name", "string", "NewNode", []),
                       MetaModelField("priority", "integer", 0, []),
                       MetaModelField("cmd_args", "string", "", [])])
meta_component_instance = MetaModel("ComponentInstance",
                                    str(uuid.uuid4()),
                                    [MetaModelField("name", "string", "NewComponentInstance", []),
                                     MetaModelField("scheduling_scheme", "string", "FIFO",
                                                    ["FIFO",
                                                     "PFIFO",
                                                     "EDF"]),
                                     MetaModelField("periodic_logging", "boolean", True, []),
                                     MetaModelField("periodic_log_unit", "integer", 1000, [])])

# Containment Hierarchy in ROSMOD
project_software_containment = MetaContainment(str(uuid.uuid4()),
                                               meta_project.uuid, meta_software.uuid, "1")
project_hardware_containment = MetaContainment(str(uuid.uuid4()),
                                               meta_project.uuid, meta_hardware.uuid, "0..*")
project_deployment_containment = MetaContainment(str(uuid.uuid4()),
                                                 meta_project.uuid, meta_deployment.uuid, "0..*")
software_package_containment = MetaContainment(str(uuid.uuid4()),
                                               meta_software.uuid, meta_package.uuid, "1..*")
package_message_containment = MetaContainment(str(uuid.uuid4()),
                                              meta_package.uuid, meta_message.uuid, "0..*")
package_service_containment = MetaContainment(str(uuid.uuid4()),
                                              meta_package.uuid, meta_service.uuid, "0..*")
package_component_containment = MetaContainment(str(uuid.uuid4()),
                                                meta_package.uuid, meta_component.uuid, "0..*")
component_timer_containment = MetaContainment(str(uuid.uuid4()),
                                              meta_component.uuid, meta_timer.uuid, "0..*")
component_client_containment = MetaContainment(str(uuid.uuid4()),
                                               meta_component.uuid, meta_client.uuid, "0..*")
component_server_containment = MetaContainment(str(uuid.uuid4()),
                                               meta_component.uuid, meta_server.uuid, "0..*")
component_publisher_containment = MetaContainment(str(uuid.uuid4()),
                                                  meta_component.uuid, meta_publisher.uuid, "0..*")
component_subscriber_containment = MetaContainment(str(uuid.uuid4()),
                                                   meta_component.uuid, meta_subscriber.uuid, "0..*")
hardware_host_containment = MetaContainment(str(uuid.uuid4()),
                                            meta_hardware.uuid, meta_host.uuid, "0..*")
deployment_node_containment = MetaContainment(str(uuid.uuid4()),
                                              meta_deployment.uuid, meta_node.uuid, "0..*")
node_componentinstance_containment = MetaContainment(str(uuid.uuid4()),
                                                     meta_node.uuid,
                                                     meta_component_instance.uuid, "0..*")

# Pointer Hierarchy in ROSMOD
client_service_pointer = MetaPointer("service_reference",
                                     str(uuid.uuid4()), meta_client.uuid, meta_service.uuid)
server_service_pointer = MetaPointer("service_reference",
                                     str(uuid.uuid4()), meta_server.uuid, meta_service.uuid)
publisher_message_pointer = MetaPointer("message_reference",
                                        str(uuid.uuid4()), meta_publisher.uuid, meta_message.uuid)
subscriber_message_pointer = MetaPointer("message_reference",
                                         str(uuid.uuid4()), meta_subscriber.uuid, meta_message.uuid)
deployment_hardware_pointer = MetaPointer("hardware_reference",
                                          str(uuid.uuid4()), meta_deployment.uuid, meta_hardware.uuid)
node_host_pointer = MetaPointer("host_reference",
                                str(uuid.uuid4()), meta_node.uuid, meta_host.uuid)
componentinstance_component_pointer = MetaPointer("component_reference",
                                                  str(uuid.uuid4()),
                                                  meta_component_instance.uuid,
                                                  meta_component.uuid)

meta_list = []
meta_list.append([meta_project, meta_software, meta_package, meta_component, meta_message,
                  meta_service, meta_client, meta_server, meta_publisher, meta_subscriber,
                  meta_timer, meta_hardware, meta_host, meta_deployment, meta_node,
                  meta_component_instance, project_software_containment,
                  project_hardware_containment, project_deployment_containment,
                  software_package_containment, package_message_containment,
                  package_service_containment, package_component_containment,
                  component_timer_containment, component_client_containment,
                  component_server_containment, component_publisher_containment,
                  component_subscriber_containment, hardware_host_containment,
                  deployment_node_containment, node_componentinstance_containment,
                  client_service_pointer, server_service_pointer, publisher_message_pointer,
                  subscriber_message_pointer, deployment_hardware_pointer, node_host_pointer,
                  componentinstance_component_pointer])
for item in meta_list[0]:
    save(item)
dictStr = json.dumps(meta_dictionary, indent=4)
with open("test_mm", 'w') as f:
    f.write(dictStr)

# TEST CASES:

# Model Classes
Hardware = ModelFactory(meta_hardware)
Deployment = ModelFactory(meta_deployment)

print meta_dictionary[deployment_hardware_pointer.src]["name"]
print meta_dictionary[deployment_hardware_pointer.dst]["name"]

setattr(eval(meta_dictionary[deployment_hardware_pointer.src]["name"]),
        deployment_hardware_pointer.name,
        meta_dictionary[deployment_hardware_pointer.dst])

print vars(Deployment)
        

# Model Objects
new_hardware = Hardware(name="my_hardware")
new_deployment = Deployment(name="my_deployment")

print new_deployment.hardware_reference
