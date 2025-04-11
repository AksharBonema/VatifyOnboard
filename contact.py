# contact.py

import streamlit as st
import streamlit.components.v1 as components

def render_contact_page():
    st.title("Contact Us")
    st.write("If you have any questions or need assistance, please fill out the contact form below and we will get back to you as soon as possible.")

    # HTML and JavaScript for EmailJS integration.
    # Make sure the form field names match those used in your EmailJS template.
    html_code = """
    <!DOCTYPE html>
    <html>
      <head>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/emailjs-com@2/dist/email.min.js"></script>
        <script type="text/javascript">
          (function(){
              emailjs.init("crQGiu0ucP1cZAT9D"); // Replace with your actual EmailJS user ID
          })();
        </script>
        <style>
          body {font-family: Arial, sans-serif; margin: 0; padding: 20px;}
          input, textarea {width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px;}
          input[type="submit"] {background-color: #4CAF50; color: white; border: none; cursor: pointer;}
          input[type="submit"]:hover {background-color: #45a049;}
          label {font-weight: bold; margin-top: 10px; display: block;}
          #status {margin-top: 10px; font-style: italic; color: #555;}
        </style>
      </head>
      <body>
        <form id="contact-form">
          <input type="hidden" name="contact_number" value="0" />
          
          <label for="from_name">Your Name:</label>
          <input type="text" id="from_name" name="from_name" placeholder="Your Name" required />

          <label for="email">Your Email:</label>
          <input type="email" id="email" name="email" placeholder="Your Email" required />

          <label for="message">Your Message:</label>
          <textarea id="message" name="message" placeholder="Enter your message here" required style="height:100px;"></textarea>

          <input type="submit" value="Send" />
        </form>
        <div id="status"></div>
        <script type="text/javascript">
          document.getElementById('contact-form').addEventListener('submit', function(event) {
            event.preventDefault();
            var form = this;
            // Generate a random number for the contact_number field.
            form.contact_number.value = Math.floor(Math.random() * 100000);
            // Display "Sending..." while the email is being sent
            document.getElementById('status').innerHTML = 'Sending...';
            
            // Send the form using EmailJS.
            emailjs.sendForm('service_xc5obyq', 'template_g00ck7h', form)
              .then(function() {
                document.getElementById('status').innerHTML = 'Your message has been sent!';
                // Reset the form after sending
                form.reset();
              }, function(error) {
                document.getElementById('status').innerHTML = 'FAILED: ' + JSON.stringify(error);
              });
          });
        </script>
      </body>
    </html>
    """
    components.html(html_code, height=550)
