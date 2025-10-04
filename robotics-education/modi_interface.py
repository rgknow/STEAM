"""
Luxrobo Modi Module Interface
Hardware abstraction layer for Luxrobo Modi master kit components
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime
import serial
import time

from agents.base_agent import AgeGroup


class ModuleType(Enum):
    """Types of Luxrobo Modi modules."""
    ENVIRONMENT = "environment"
    IMU = "imu"
    LED = "led"
    SPEAKER = "speaker"
    BUTTON = "button"
    DIAL = "dial"
    NETWORK = "network"
    DISPLAY = "display"
    MOTOR = "motor"
    IR_SENSOR = "ir_sensor"
    TOF_SENSOR = "tof_sensor"
    BATTERY = "battery"


class ConnectionStatus(Enum):
    """Connection status for modules."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ModuleCapability:
    """Defines capabilities of a module."""
    can_read: bool = False
    can_write: bool = False
    has_feedback: bool = False
    supports_realtime: bool = False
    data_types: List[str] = field(default_factory=list)
    age_appropriate: List[AgeGroup] = field(default_factory=list)
    safety_level: int = 1  # 1=very safe, 5=requires supervision


@dataclass
class SensorReading:
    """Sensor data reading."""
    module_id: int
    module_type: ModuleType
    timestamp: datetime
    data: Dict[str, Any]
    unit: Optional[str] = None
    quality: float = 1.0  # 0-1 reliability score


@dataclass
class ModuleCommand:
    """Command to send to a module."""
    module_id: int
    module_type: ModuleType
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_response: bool = True
    timeout: float = 5.0


class ModiModuleInterface:
    """Interface for individual Modi modules."""
    
    def __init__(self, module_id: int, module_type: ModuleType):
        self.module_id = module_id
        self.module_type = module_type
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.last_data = None
        self.capabilities = self._get_module_capabilities()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(f"modi_{module_type.value}_{module_id}")
        
    def _get_module_capabilities(self) -> ModuleCapability:
        """Get capabilities for this module type."""
        capabilities_map = {
            ModuleType.ENVIRONMENT: ModuleCapability(
                can_read=True,
                has_feedback=True,
                supports_realtime=True,
                data_types=["temperature", "humidity", "brightness", "red", "green", "blue"],
                age_appropriate=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.IMU: ModuleCapability(
                can_read=True,
                has_feedback=True,
                supports_realtime=True,
                data_types=["acceleration_x", "acceleration_y", "acceleration_z", "gyro_x", "gyro_y", "gyro_z"],
                age_appropriate=[AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.LED: ModuleCapability(
                can_write=True,
                has_feedback=False,
                data_types=["red", "green", "blue", "brightness"],
                age_appropriate=[AgeGroup.EARLY_YEARS, AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.SPEAKER: ModuleCapability(
                can_write=True,
                has_feedback=False,
                data_types=["frequency", "volume", "duration"],
                age_appropriate=[AgeGroup.EARLY_YEARS, AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=2
            ),
            ModuleType.BUTTON: ModuleCapability(
                can_read=True,
                has_feedback=True,
                supports_realtime=True,
                data_types=["pressed", "click_count"],
                age_appropriate=[AgeGroup.EARLY_YEARS, AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.DIAL: ModuleCapability(
                can_read=True,
                has_feedback=True,
                supports_realtime=True,
                data_types=["degree", "turnspeed"],
                age_appropriate=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.NETWORK: ModuleCapability(
                can_read=True,
                can_write=True,
                has_feedback=True,
                data_types=["wifi_strength", "connected", "data_received", "data_sent"],
                age_appropriate=[AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=3
            ),
            ModuleType.DISPLAY: ModuleCapability(
                can_write=True,
                has_feedback=False,
                data_types=["text", "image", "pixel", "brightness"],
                age_appropriate=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.MOTOR: ModuleCapability(
                can_write=True,
                can_read=True,
                has_feedback=True,
                supports_realtime=True,
                data_types=["speed", "degree", "torque"],
                age_appropriate=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=3
            ),
            ModuleType.IR_SENSOR: ModuleCapability(
                can_read=True,
                has_feedback=True,
                supports_realtime=True,
                data_types=["proximity"],
                age_appropriate=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.TOF_SENSOR: ModuleCapability(
                can_read=True,
                has_feedback=True,
                supports_realtime=True,
                data_types=["distance"],
                age_appropriate=[AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=1
            ),
            ModuleType.BATTERY: ModuleCapability(
                can_read=True,
                has_feedback=True,
                data_types=["level", "voltage", "charging"],
                age_appropriate=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
                safety_level=2
            )
        }
        
        return capabilities_map.get(self.module_type, ModuleCapability())
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler for module events."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove event handler."""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    async def _trigger_event(self, event_type: str, data: Any):
        """Trigger event handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
    
    async def read_data(self) -> Optional[SensorReading]:
        """Read data from module."""
        if not self.capabilities.can_read:
            raise ValueError(f"Module {self.module_type.value} cannot read data")
        
        # Module-specific reading logic would go here
        # For now, return simulated data based on module type
        data = await self._simulate_read_data()
        
        if data:
            reading = SensorReading(
                module_id=self.module_id,
                module_type=self.module_type,
                timestamp=datetime.now(),
                data=data
            )
            
            self.last_data = reading
            await self._trigger_event("data_received", reading)
            return reading
        
        return None
    
    async def write_command(self, command: ModuleCommand) -> bool:
        """Send command to module."""
        if not self.capabilities.can_write:
            raise ValueError(f"Module {self.module_type.value} cannot receive commands")
        
        try:
            # Module-specific command logic would go here
            success = await self._simulate_write_command(command)
            
            if success:
                await self._trigger_event("command_sent", command)
            else:
                await self._trigger_event("command_failed", command)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            await self._trigger_event("command_error", {"command": command, "error": str(e)})
            return False
    
    async def _simulate_read_data(self) -> Dict[str, Any]:
        """Simulate reading data from module (placeholder for actual hardware interface)."""
        import random
        
        simulation_data = {
            ModuleType.ENVIRONMENT: {
                "temperature": round(random.uniform(18.0, 28.0), 1),
                "humidity": round(random.uniform(30.0, 80.0), 1),
                "brightness": random.randint(0, 100),
                "red": random.randint(0, 255),
                "green": random.randint(0, 255),
                "blue": random.randint(0, 255)
            },
            ModuleType.IMU: {
                "acceleration_x": round(random.uniform(-2.0, 2.0), 2),
                "acceleration_y": round(random.uniform(-2.0, 2.0), 2),
                "acceleration_z": round(random.uniform(8.0, 12.0), 2),
                "gyro_x": round(random.uniform(-180.0, 180.0), 2),
                "gyro_y": round(random.uniform(-180.0, 180.0), 2),
                "gyro_z": round(random.uniform(-180.0, 180.0), 2)
            },
            ModuleType.BUTTON: {
                "pressed": random.choice([True, False]),
                "click_count": random.randint(0, 5)
            },
            ModuleType.DIAL: {
                "degree": random.randint(0, 360),
                "turnspeed": round(random.uniform(-50.0, 50.0), 1)
            },
            ModuleType.IR_SENSOR: {
                "proximity": random.randint(0, 100)
            },
            ModuleType.TOF_SENSOR: {
                "distance": round(random.uniform(2.0, 400.0), 1)
            },
            ModuleType.BATTERY: {
                "level": random.randint(20, 100),
                "voltage": round(random.uniform(3.2, 4.2), 2),
                "charging": random.choice([True, False])
            },
            ModuleType.MOTOR: {
                "speed": random.randint(-100, 100),
                "degree": random.randint(0, 360),
                "torque": round(random.uniform(0.0, 1.0), 2)
            }
        }
        
        return simulation_data.get(self.module_type, {})
    
    async def _simulate_write_command(self, command: ModuleCommand) -> bool:
        """Simulate sending command to module."""
        # Simulate command processing time
        await asyncio.sleep(0.1)
        
        # Validate command parameters based on module type
        valid_commands = {
            ModuleType.LED: ["set_color", "set_brightness", "turn_on", "turn_off"],
            ModuleType.SPEAKER: ["play_tone", "play_melody", "set_volume"],
            ModuleType.DISPLAY: ["show_text", "show_image", "clear", "set_brightness"],
            ModuleType.MOTOR: ["set_speed", "rotate", "stop", "set_torque"]
        }
        
        if self.module_type in valid_commands:
            if command.command in valid_commands[self.module_type]:
                self.logger.info(f"Command {command.command} sent to {self.module_type.value}")
                return True
            else:
                self.logger.warning(f"Invalid command {command.command} for {self.module_type.value}")
                return False
        
        return True  # Default success for other modules
    
    def get_age_appropriate_methods(self, age_group: AgeGroup) -> List[str]:
        """Get methods appropriate for a specific age group."""
        if age_group not in self.capabilities.age_appropriate:
            return []
        
        # Return simplified method lists based on age
        if age_group == AgeGroup.EARLY_YEARS:
            return self._get_simple_methods()
        elif age_group == AgeGroup.ELEMENTARY:
            return self._get_basic_methods()
        elif age_group == AgeGroup.MIDDLE_SCHOOL:
            return self._get_intermediate_methods()
        else:
            return self._get_advanced_methods()
    
    def _get_simple_methods(self) -> List[str]:
        """Get very simple methods for early years."""
        simple_methods = {
            ModuleType.LED: ["turn_on", "turn_off", "make_red", "make_blue", "make_green"],
            ModuleType.SPEAKER: ["beep", "play_happy_sound"],
            ModuleType.BUTTON: ["is_pressed", "wait_for_press"],
            ModuleType.DISPLAY: ["show_smiley", "show_text"]
        }
        return simple_methods.get(self.module_type, [])
    
    def _get_basic_methods(self) -> List[str]:
        """Get basic methods for elementary age."""
        basic_methods = {
            ModuleType.LED: ["set_color", "set_brightness", "blink"],
            ModuleType.SPEAKER: ["play_tone", "play_melody", "set_volume"],
            ModuleType.BUTTON: ["is_pressed", "get_clicks", "wait_for_press"],
            ModuleType.DISPLAY: ["show_text", "show_number", "clear"],
            ModuleType.MOTOR: ["move_forward", "move_backward", "turn_left", "turn_right", "stop"],
            ModuleType.ENVIRONMENT: ["get_temperature", "get_light_level"],
            ModuleType.IR_SENSOR: ["detect_object", "get_distance"]
        }
        return basic_methods.get(self.module_type, [])
    
    def _get_intermediate_methods(self) -> List[str]:
        """Get intermediate methods for middle school."""
        intermediate_methods = {
            ModuleType.LED: ["set_rgb", "fade", "pulse", "rainbow"],
            ModuleType.SPEAKER: ["play_frequency", "play_chord", "modulate"],
            ModuleType.MOTOR: ["set_speed", "rotate_degrees", "set_acceleration"],
            ModuleType.IMU: ["get_acceleration", "get_rotation", "detect_tilt"],
            ModuleType.ENVIRONMENT: ["monitor_changes", "log_data", "trigger_threshold"],
            ModuleType.DISPLAY: ["draw_pixel", "draw_line", "show_graph"]
        }
        return intermediate_methods.get(self.module_type, [])
    
    def _get_advanced_methods(self) -> List[str]:
        """Get advanced methods for high school and above."""
        advanced_methods = {
            ModuleType.LED: ["set_hsv", "animate", "sync_with_data"],
            ModuleType.MOTOR: ["pid_control", "encoder_feedback", "torque_control"],
            ModuleType.IMU: ["sensor_fusion", "quaternion_rotation", "calibrate"],
            ModuleType.NETWORK: ["send_data", "receive_data", "setup_server"],
            ModuleType.ENVIRONMENT: ["statistical_analysis", "predictive_modeling"]
        }
        return advanced_methods.get(self.module_type, [])
    
    def generate_code_template(self, age_group: AgeGroup, method: str) -> str:
        """Generate age-appropriate code template for a method."""
        if age_group == AgeGroup.EARLY_YEARS:
            return self._generate_simple_template(method)
        elif age_group == AgeGroup.ELEMENTARY:
            return self._generate_basic_template(method)
        elif age_group == AgeGroup.MIDDLE_SCHOOL:
            return self._generate_intermediate_template(method)
        else:
            return self._generate_advanced_template(method)
    
    def _generate_simple_template(self, method: str) -> str:
        """Generate very simple code template."""
        templates = {
            "turn_on": f"# Make the light turn on\n{self.module_type.value}.turn_on()",
            "beep": f"# Make a beep sound\n{self.module_type.value}.beep()",
            "is_pressed": f"# Check if button is pressed\nif {self.module_type.value}.is_pressed():\n    print('Button pressed!')"
        }
        return templates.get(method, f"# Use {method}\n{self.module_type.value}.{method}()")
    
    def _generate_basic_template(self, method: str) -> str:
        """Generate basic code template."""
        templates = {
            "set_color": f"""# Set LED color
{self.module_type.value}.set_color(red=255, green=0, blue=0)  # Red color""",
            "play_tone": f"""# Play a musical tone
{self.module_type.value}.play_tone(frequency=440, duration=1.0)  # A note for 1 second""",
            "move_forward": f"""# Move robot forward
{self.module_type.value}.move_forward(speed=50)  # Move at half speed"""
        }
        return templates.get(method, f"# Use {method}\n{self.module_type.value}.{method}()")
    
    def _generate_intermediate_template(self, method: str) -> str:
        """Generate intermediate code template."""
        templates = {
            "set_rgb": f"""# Set LED using RGB values
for i in range(256):
    {self.module_type.value}.set_rgb(red=i, green=255-i, blue=0)
    time.sleep(0.01)  # Create color transition""",
            "get_acceleration": f"""# Read acceleration data
accel_data = {self.module_type.value}.get_acceleration()
print(f"X: {{accel_data['x']:.2f}}, Y: {{accel_data['y']:.2f}}, Z: {{accel_data['z']:.2f}}")"""
        }
        return templates.get(method, f"# Use {method}\nresult = {self.module_type.value}.{method}()")
    
    def _generate_advanced_template(self, method: str) -> str:
        """Generate advanced code template."""
        templates = {
            "pid_control": f"""# PID motor control
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.prev_error = 0
        self.integral = 0
    
    def calculate(self, setpoint, measured_value, dt):
        error = setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output

pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
{self.module_type.value}.set_pid_controller(pid)""",
            "sensor_fusion": f"""# Sensor fusion algorithm
import numpy as np

def sensor_fusion(accel_data, gyro_data, dt=0.01):
    # Complementary filter
    alpha = 0.98
    angle_accel = np.arctan2(accel_data['y'], accel_data['z'])
    angle_gyro = angle_accel + gyro_data['x'] * dt
    fused_angle = alpha * angle_gyro + (1 - alpha) * angle_accel
    return fused_angle

angle = sensor_fusion({self.module_type.value}.get_acceleration(), 
                     {self.module_type.value}.get_gyroscope())"""
        }
        return templates.get(method, f"# Advanced {method} implementation\n{self.module_type.value}.{method}()")


class ModiKitManager:
    """Manager for the complete Modi kit with multiple modules."""
    
    def __init__(self):
        self.modules: Dict[int, ModiModuleInterface] = {}
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.serial_connection = None
        self.logger = logging.getLogger("modi_kit_manager")
        self.project_context = None
        
    async def initialize_kit(self, port: str = "auto") -> bool:
        """Initialize connection to Modi kit."""
        try:
            if port == "auto":
                port = self._detect_modi_port()
            
            if port:
                # In real implementation, this would establish serial connection
                self.connection_status = ConnectionStatus.CONNECTED
                await self._discover_modules()
                self.logger.info(f"Modi kit initialized with {len(self.modules)} modules")
                return True
            else:
                self.logger.error("No Modi kit detected")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Modi kit: {e}")
            self.connection_status = ConnectionStatus.ERROR
            return False
    
    def _detect_modi_port(self) -> Optional[str]:
        """Detect Modi kit USB port."""
        # Placeholder for actual port detection
        # In real implementation, would scan for USB-C connection
        return "/dev/ttyUSB0"  # Simulated port
    
    async def _discover_modules(self):
        """Discover connected modules."""
        # Simulate discovering modules - in real implementation would query hardware
        discovered_modules = [
            (1, ModuleType.ENVIRONMENT),
            (2, ModuleType.IMU),
            (3, ModuleType.LED),
            (4, ModuleType.SPEAKER),
            (5, ModuleType.BUTTON),
            (6, ModuleType.DIAL),
            (7, ModuleType.NETWORK),
            (8, ModuleType.DISPLAY),
            (9, ModuleType.MOTOR),
            (10, ModuleType.MOTOR),
            (11, ModuleType.MOTOR),
            (12, ModuleType.MOTOR),
            (13, ModuleType.IR_SENSOR),
            (14, ModuleType.TOF_SENSOR),
            (15, ModuleType.BATTERY)
        ]
        
        for module_id, module_type in discovered_modules:
            module = ModiModuleInterface(module_id, module_type)
            module.connection_status = ConnectionStatus.CONNECTED
            self.modules[module_id] = module
            self.logger.info(f"Discovered {module_type.value} module (ID: {module_id})")
    
    def get_module(self, module_id: int) -> Optional[ModiModuleInterface]:
        """Get module by ID."""
        return self.modules.get(module_id)
    
    def get_modules_by_type(self, module_type: ModuleType) -> List[ModiModuleInterface]:
        """Get all modules of a specific type."""
        return [module for module in self.modules.values() if module.module_type == module_type]
    
    def get_available_modules(self, age_group: AgeGroup) -> List[ModiModuleInterface]:
        """Get modules appropriate for an age group."""
        appropriate_modules = []
        for module in self.modules.values():
            if age_group in module.capabilities.age_appropriate:
                appropriate_modules.append(module)
        return appropriate_modules
    
    async def read_all_sensors(self) -> Dict[int, SensorReading]:
        """Read data from all sensor modules."""
        readings = {}
        
        tasks = []
        for module_id, module in self.modules.items():
            if module.capabilities.can_read:
                tasks.append(self._read_module_data(module_id, module))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                readings[result.module_id] = result
        
        return readings
    
    async def _read_module_data(self, module_id: int, module: ModiModuleInterface) -> Optional[SensorReading]:
        """Read data from a specific module."""
        try:
            return await module.read_data()
        except Exception as e:
            self.logger.error(f"Failed to read from module {module_id}: {e}")
            return None
    
    def generate_project_code(self, project_spec: Dict[str, Any], age_group: AgeGroup) -> str:
        """Generate complete project code based on specifications."""
        code_parts = [
            "# Modi Kit Project Code",
            "# Generated automatically for STEAM learning",
            "",
            "import time",
            "import modi_kit",
            "",
            "# Initialize Modi kit",
            "kit = modi_kit.ModiKitManager()",
            "await kit.initialize_kit()",
            ""
        ]
        
        # Add module initialization
        used_modules = project_spec.get("modules", [])
        for module_spec in used_modules:
            module_type = module_spec["type"]
            module_var = module_spec.get("name", module_type.lower())
            
            modules_of_type = self.get_modules_by_type(ModuleType(module_type))
            if modules_of_type:
                module_id = modules_of_type[0].module_id
                code_parts.append(f"{module_var} = kit.get_module({module_id})")
        
        code_parts.append("")
        
        # Add main project logic
        main_logic = project_spec.get("main_logic", [])
        for logic_step in main_logic:
            code_parts.append(f"# {logic_step['description']}")
            code_parts.append(logic_step["code"])
            code_parts.append("")
        
        return "\n".join(code_parts)
    
    def get_kit_status(self) -> Dict[str, Any]:
        """Get status of the entire kit."""
        module_status = {}
        for module_id, module in self.modules.items():
            module_status[module_id] = {
                "type": module.module_type.value,
                "status": module.connection_status.value,
                "capabilities": {
                    "can_read": module.capabilities.can_read,
                    "can_write": module.capabilities.can_write,
                    "safety_level": module.capabilities.safety_level
                }
            }
        
        return {
            "connection_status": self.connection_status.value,
            "total_modules": len(self.modules),
            "modules": module_status,
            "battery_level": self._get_battery_level()
        }
    
    def _get_battery_level(self) -> Optional[int]:
        """Get battery level from battery module."""
        battery_modules = self.get_modules_by_type(ModuleType.BATTERY)
        if battery_modules and battery_modules[0].last_data:
            return battery_modules[0].last_data.data.get("level")
        return None
    
    async def cleanup(self):
        """Clean up resources and disconnect."""
        for module in self.modules.values():
            module.connection_status = ConnectionStatus.DISCONNECTED
        
        if self.serial_connection:
            # Close serial connection
            pass
        
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.logger.info("Modi kit disconnected")


# Example usage functions for different age groups
def create_simple_project_example():
    """Create a simple project example for young learners."""
    return {
        "title": "Traffic Light",
        "age_group": "elementary",
        "modules": [
            {"type": "led", "name": "traffic_light"},
            {"type": "button", "name": "crossing_button"}
        ],
        "main_logic": [
            {
                "description": "Make traffic light turn red",
                "code": "traffic_light.set_color(red=255, green=0, blue=0)\ntime.sleep(3)"
            },
            {
                "description": "Wait for button press",
                "code": "crossing_button.wait_for_press()\nprint('Pedestrian crossing!')"
            },
            {
                "description": "Change to green light",
                "code": "traffic_light.set_color(red=0, green=255, blue=0)\ntime.sleep(5)"
            }
        ]
    }


def create_intermediate_project_example():
    """Create an intermediate project for middle school learners."""
    return {
        "title": "Weather Station",
        "age_group": "middle_school",
        "modules": [
            {"type": "environment", "name": "weather_sensor"},
            {"type": "display", "name": "screen"},
            {"type": "network", "name": "wifi"}
        ],
        "main_logic": [
            {
                "description": "Read weather data continuously",
                "code": """while True:
    data = await weather_sensor.read_data()
    temperature = data.data['temperature']
    humidity = data.data['humidity']
    
    # Display on screen
    screen.show_text(f'Temp: {temperature}°C\\nHumidity: {humidity}%')
    
    # Send data to cloud (if connected)
    if wifi.is_connected():
        wifi.send_data({'temp': temperature, 'humidity': humidity})
    
    time.sleep(60)  # Update every minute"""
            }
        ]
    }


def create_advanced_project_example():
    """Create an advanced project for high school learners."""
    return {
        "title": "Autonomous Robot",
        "age_group": "high_school",
        "modules": [
            {"type": "motor", "name": "left_motor"},
            {"type": "motor", "name": "right_motor"},
            {"type": "tof_sensor", "name": "distance_sensor"},
            {"type": "imu", "name": "orientation_sensor"}
        ],
        "main_logic": [
            {
                "description": "Autonomous navigation with obstacle avoidance",
                "code": """class AutonomousRobot:
    def __init__(self, left_motor, right_motor, distance_sensor, imu):
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.distance_sensor = distance_sensor
        self.imu = imu
        self.target_heading = 0
    
    async def navigate(self):
        while True:
            # Read sensors
            distance_data = await self.distance_sensor.read_data()
            imu_data = await self.imu.read_data()
            
            distance = distance_data.data['distance']
            heading = imu_data.data['gyro_z']
            
            if distance < 20:  # Obstacle detected
                await self.avoid_obstacle()
            else:
                await self.move_forward()
            
            await self.correct_heading(heading)
            await asyncio.sleep(0.1)
    
    async def avoid_obstacle(self):
        # Stop and turn
        await self.left_motor.write_command(ModuleCommand(
            self.left_motor.module_id, ModuleType.MOTOR, "stop"
        ))
        await self.right_motor.write_command(ModuleCommand(
            self.right_motor.module_id, ModuleType.MOTOR, "stop"
        ))
        
        # Turn right
        await self.left_motor.write_command(ModuleCommand(
            self.left_motor.module_id, ModuleType.MOTOR, "set_speed", {"speed": 50}
        ))
        await self.right_motor.write_command(ModuleCommand(
            self.right_motor.module_id, ModuleType.MOTOR, "set_speed", {"speed": -50}
        ))
        
        await asyncio.sleep(1)  # Turn for 1 second

robot = AutonomousRobot(left_motor, right_motor, distance_sensor, orientation_sensor)
await robot.navigate()"""
            }
        ]
    }


# Main example usage
async def main():
    """Example usage of Modi kit interface."""
    print("=== Modi Kit Interface Demo ===")
    
    # Initialize kit
    kit = ModiKitManager()
    success = await kit.initialize_kit()
    
    if success:
        print(f"Kit initialized successfully!")
        
        # Get kit status
        status = kit.get_kit_status()
        print(f"Total modules: {status['total_modules']}")
        
        # Demonstrate age-appropriate modules
        elementary_modules = kit.get_available_modules(AgeGroup.ELEMENTARY)
        print(f"Modules appropriate for elementary: {len(elementary_modules)}")
        
        # Generate project code
        simple_project = create_simple_project_example()
        code = kit.generate_project_code(simple_project, AgeGroup.ELEMENTARY)
        print(f"\nGenerated project code:\n{code}")
        
        # Read sensor data
        readings = await kit.read_all_sensors()
        print(f"\nSensor readings: {len(readings)}")
        
        await kit.cleanup()
    else:
        print("Failed to initialize kit")


if __name__ == "__main__":
    asyncio.run(main())