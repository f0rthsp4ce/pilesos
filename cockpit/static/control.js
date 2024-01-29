document.addEventListener("DOMContentLoaded", function () {
  // Function to send the whole state of inputs to the server
  function sendControl(control) {
    const payload = JSON.stringify(control);
    console.debug("sent: ", payload);
    socket.send(payload);
  }

  // Connect to the WebSocket server
  const socket = new WebSocket(`ws://${window.location.host}/ws`);
  socket.addEventListener("error", function (event) {
    console.error("WebSocket error:", event);
  });
  window.addEventListener("unload", function () {
    socket.close();
  });

  // Define telemetry elements
  const batteryVolts = document.getElementById("batteryVolts");
  const batteryPercent = document.getElementById("batteryPercent");
  const batteryProgressbar = document.getElementById("batteryProgressbar");

  // Telemetry receiver
  socket.addEventListener("message", function (event) {
    console.info("recv: ", event.data);
    const telemetry = JSON.parse(event.data);
    batteryVolts.textContent = `${telemetry.battery.volts.toFixed(1)}V`;
    batteryPercent.textContent = `${telemetry.battery.percent}%`;
    batteryProgressbar.style.width = `${telemetry.battery.percent}%`;

    // update colors
    let p = telemetry.battery.percent;
    let c = "--battery-unknown";
    switch (true) {
      case (p < 20):
        c = "--battery-low"
        break;
      case (p > 100):
        c = "--battery-overcharge"
        break
      default:
        c = "--battery-full"
    }
    document.documentElement.style.setProperty(
      "--battery",
      getComputedStyle(document.body).getPropertyValue(c)
    );
  });

  // Define control elements
  const joystick = document.getElementById("joystick");
  const beepButton = document.getElementById("beepButton");
  const lightsSwitch = document.getElementById("lightsSwitch");

  // Initialize NippleJS
  const joystick_manager = nipplejs.create({
    zone: document.getElementById("joystick"),
    mode: "static",
    color: getComputedStyle(document.documentElement).getPropertyValue(
      "--accent"
    ),
    restJoystick: true,
    dynamicPage: true,
    size: 200,
  });

  function sendJoystickControl() {
    function filterJoystick(value) {
      let speed_divisor = 1;
      // joystick max tilt in any direction
      let value_max = 100;
      // filtering strength
      let exp = 1.33;
      // process negative tilt as well, save original number sign
      let orig_sign = Math.sign(value);
      value = Math.abs(value);
      // calculate filtered value
      let powed = Math.pow(value, exp) || 0;
      // limit to original range of values
      let pow_maximum = Math.pow(value_max, exp);
      let limited = (powed / pow_maximum) * value_max;
      // restore original sign
      return (orig_sign * limited) / speed_divisor;
    }
    function mapJoystickToTracks(joystickX, joystickY) {
      // Convert (X, Y) from joystick to (L, R) throttles for each motor in two-track vehicle (tank, vacuum cleaner)
      // nipplejs inverts joystick Y
      joystickY = -joystickY;
      const maxJoystickValue = 100;
      const maxTrackThrottle = 255;

      // Map joystick values to track throttles
      let leftTrackThrottle =
        (maxTrackThrottle * (joystickY + joystickX)) / maxJoystickValue;
      let rightTrackThrottle =
        (maxTrackThrottle * (joystickY - joystickX)) / maxJoystickValue;
      
      if (joystickY < 0) {
        [leftTrackThrottle, rightTrackThrottle] = [rightTrackThrottle, leftTrackThrottle]
      }
      
      // Ensure throttles are within the valid range
      const clampedLeftTrackThrottle = Math.max(
        -maxTrackThrottle,
        Math.min(maxTrackThrottle, leftTrackThrottle)
      );
      const clampedRightTrackThrottle = Math.max(
        -maxTrackThrottle,
        Math.min(maxTrackThrottle, rightTrackThrottle)
      );

      return [
        Math.round(clampedLeftTrackThrottle),
        Math.round(clampedRightTrackThrottle),
      ];
    }

    let x = joystick_manager[0].frontPosition.x;
    let y = joystick_manager[0].frontPosition.y;
    let [left, right] = mapJoystickToTracks(
      filterJoystick(x),
      filterJoystick(y)
    );
    sendControl({ wheels: { left: left, right: right } });
  }

  // Event listener for joystick movement
  joystick_manager.on("move", sendJoystickControl);
  joystick_manager.on("end", function () {
    sendControl({ wheels: { left: 0, right: 0 } });
  });

  const joystickKeyState = {
    w: false,
    s: false,
    a: false,
    d: false,
  };

  const joystickSpeed = 1; // Adjust the speed as needed
  const maxVelocity = 100; // Adjust the maximum velocity as needed
  const acceleration = 2; // Adjust the acceleration as needed
  const joystickRadius = 100; // Adjust the joystick radius as needed

  let velocityX = 0;
  let velocityY = 0;
  let prevPosition = { x: 0, y: 0 };

  function moveJoystickWithKeyboard() {
    const deltaX = (joystickKeyState.d ? 1 : 0) - (joystickKeyState.a ? 1 : 0);
    const deltaY = (joystickKeyState.s ? 1 : 0) - (joystickKeyState.w ? 1 : 0);
    if (!deltaX && !deltaY) {
      // Reset velocity and joystick position when no keys are pressed
      velocityX = 0;
      velocityY = 0;
    } else {
      // Update velocity based on key presses
      velocityX += deltaX * acceleration;
      velocityY += deltaY * acceleration;

      // Limit the velocity to the maximum value
      velocityX = Math.min(Math.max(velocityX, -maxVelocity), maxVelocity);
      velocityY = Math.min(Math.max(velocityY, -maxVelocity), maxVelocity);
    }

    // Update joystick position based on velocity
    const newDeltaX = velocityX * joystickSpeed;
    const newDeltaY = velocityY * joystickSpeed;

    // Limit the joystick movement to a circle
    const distance = Math.sqrt(newDeltaX ** 2 + newDeltaY ** 2);
    let finalX = 0;
    let finalY = 0;
    if (distance > joystickRadius) {
      const angle = Math.atan2(newDeltaY, newDeltaX);
      const clampedX = joystickRadius * Math.cos(angle);
      const clampedY = joystickRadius * Math.sin(angle);

      finalX = clampedX;
      finalY = clampedY;
    } else {
      finalX = newDeltaX;
      finalY = newDeltaY;
    }

    // update internal joystick position
    joystick_manager[0].frontPosition.x = finalX;
    joystick_manager[0].frontPosition.y = finalY;
    

    if (
      // not the same position as previous one
      (finalX !== prevPosition.x && finalY !== prevPosition.y) ||
      // or key is still being pressed
      (joystickKeyState.a || joystickKeyState.d || joystickKeyState.s || joystickKeyState.w) ||
      // or new position is 0,0 but old position is not (handle key release)
      (finalX == 0 && prevPosition.x !== 0) || (finalY == 0 && prevPosition.y !== 0)
    ) {
      // then update the joystick visually and send the data to server

      // this api is slow
      //joystick_manager[0].setPosition(sendJoystickControl, { x: finalX, y: finalY });
      // this hack is faster
      joystick_manager[0].ui.front.style.transform = `translate(${finalX}px, ${finalY}px`;
      sendJoystickControl();
      prevPosition = {x: finalX, y: finalY}
    }

    // Use requestAnimationFrame for smoother updates
    requestAnimationFrame(moveJoystickWithKeyboard);
  }

  socket.addEventListener("open", function () {
    // start the loop
    moveJoystickWithKeyboard();
  });

  // Button events
  function beepButtonPress() {
    beepButton.classList.add("active");
    sendControl({ buttons: { beep: true } });
  }
  function beepButtonRelease() {
    beepButton.classList.remove("active");
    sendControl({ buttons: { beep: false } });
  }
  beepButton.addEventListener("mousedown", beepButtonPress);
  beepButton.addEventListener("touchstart", beepButtonPress, {
    passive: true,
  });
  beepButton.addEventListener("mouseup", beepButtonRelease);
  beepButton.addEventListener("touchend", beepButtonRelease, {
    passive: true,
  });

  // Switches events
  lightsSwitch.addEventListener("change", function () {
    sendControl({ switches: { lights: lightsSwitch.checked } });
  });

  // Keyboard controls
  function handleKeyDown(event) {
    if (event.key in joystickKeyState) {
      event.preventDefault();
      joystickKeyState[event.key] = true;
    }
    if (event.key == "b") {
      event.preventDefault();
      beepButtonPress();
    }
  }

  function handleKeyUp(event) {
    if (event.key in joystickKeyState) {
      event.preventDefault();
      joystickKeyState[event.key] = false;
      // Reset velocity of the released joystick axis to zero
      if (event.key === "a" || event.key === "d") {
        velocityX = 0;
      }
      if (event.key === "w" || event.key === "s") {
        velocityY = 0;
      }
    }
    if (event.key == "b") {
      event.preventDefault();
      beepButtonRelease();
    }
  }

  // Keyboard Controls
  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
  
});
