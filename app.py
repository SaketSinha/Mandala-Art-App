import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import os
from openai import OpenAI

# Set page configuration
st.set_page_config(
    page_title="Mandala Art Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E4057;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #546E7A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .instruction-box {
        background-color: #F0F8FF;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1976D2;
        margin: 1rem 0;
    }
    .download-button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎨 Mandala Art Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform words into beautiful, printable Mandala artwork</p>', unsafe_allow_html=True)
    
    # Sidebar for API key and instructions
    with st.sidebar:
        st.markdown("### 🔑 OpenAI API Setup")
        api_key = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        if not api_key:
            st.markdown("""
            <div class="instruction-box">
                <h4>🚀 Getting Started:</h4>
                <ol>
                    <li>Get your OpenAI API key from <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI Platform</a></li>
                    <li>Enter the API key in the field above</li>
                    <li>Type an inspiring word</li>
                    <li>Generate your unique Mandala!</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📋 About")
        st.markdown("""
        This app generates beautiful Mandala-style artwork perfect for:
        - Coloring books
        - Meditation art
        - Decorative prints
        - Therapeutic coloring
        """)
        
        st.markdown("### ⚙️ Features")
        st.markdown("""
        - High-resolution output
        - Print-ready formats
        - Black & white line art
        - Symmetrical designs
        - Instant download
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💡 Enter Your Inspiration Word")
        word = st.text_input(
            "Type a word that inspires you:",
            placeholder="e.g., peace, love, nature, harmony...",
            help="Choose any word that resonates with you. The AI will create a Mandala inspired by its meaning and energy."
        )
        
        # Advanced options
        with st.expander("🎨 Advanced Options"):
            complexity = st.select_slider(
                "Complexity Level:",
                options=["Simple", "Moderate", "Detailed", "Very Detailed"],
                value="Moderate",
                help="Choose how intricate you want your Mandala to be"
            )
            
            style = st.selectbox(
                "Art Style:",
                ["Traditional Mandala", "Geometric Patterns", "Nature-Inspired", "Abstract Designs"],
                help="Select the artistic style for your Mandala"
            )
            
            size = st.selectbox(
                "Image Size:",
                ["1024x1024 (Standard)", "1792x1024 (Wide)", "1024x1792 (Tall)"],
                help="Choose the dimensions for your Mandala"
            )
        
        # Generate button
        generate_button = st.button(
            "🎨 Generate Mandala",
            type="primary",
            disabled=not (api_key and word),
            help="Click to create your unique Mandala artwork"
        )
    
    with col2:
        st.markdown("### 🖼️ Your Generated Mandala")
        
        if generate_button and api_key and word:
            with st.spinner("🎨 Creating your beautiful Mandala... This may take a moment."):
                try:
                    # Initialize OpenAI client
                    client = OpenAI(api_key=api_key)
                    
                    # Create detailed prompt for Mandala generation
                    prompt = create_mandala_prompt(word, complexity, style)
                    
                    # Parse size
                    if "1792x1024" in size:
                        image_size = "1792x1024"
                    elif "1024x1792" in size:
                        image_size = "1024x1792"
                    else:
                        image_size = "1024x1024"
                    
                    # Generate image using the latest OpenAI API
                    response = client.images.generate(
                        model="dall-e-3",  # Using DALL-E 3 for better quality
                        prompt=prompt,
                        size=image_size,
                        quality="hd",  # High quality for printing
                        n=1
                    )
                    
                    # Get the image URL
                    image_url = response.data[0].url
                    
                    # Download and display the image
                    image_response = requests.get(image_url)
                    image = Image.open(io.BytesIO(image_response.content))
                    
                    # Display the image
                    st.image(image, caption=f"Mandala inspired by: {word.title()}", use_column_width=True)
                    
                    # Convert to high-quality format for download
                    buf = io.BytesIO()
                    # Ensure RGB mode for PNG
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(buf, format='PNG', quality=95, optimize=True)
                    buf.seek(0)
                    
                    # Create download button
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"mandala_{word}_{timestamp}.png"
                    
                    st.download_button(
                        label="📥 Download High-Res PNG",
                        data=buf.getvalue(),
                        file_name=filename,
                        mime="image/png",
                        help="Download your Mandala in high resolution for printing"
                    )
                    
                    # Display generation details
                    with st.expander("📊 Generation Details"):
                        st.write(f"**Word:** {word.title()}")
                        st.write(f"**Style:** {style}")
                        st.write(f"**Complexity:** {complexity}")
                        st.write(f"**Size:** {image_size}")
                        st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        st.markdown("**Prompt Used:**")
                        st.code(prompt, language="text")
                    
                except Exception as e:
                        st.error(f"❌ Error generating Mandala: {str(e)}")
                        st.markdown("""
                        **Possible solutions:**
                        - Check your API key is correct
                        - Ensure you have sufficient OpenAI credits
                        - Try a different word or simpler complexity
                        - Check your internet connection
                        """)
        
        elif not api_key:
            st.info("🔑 Please enter your OpenAI API key in the sidebar to get started.")
        elif not word:
            st.info("💡 Please enter an inspiring word to generate your Mandala.")
    
    # Footer with printing tips
    st.markdown("---")
    st.markdown("### 🖨️ Printing Tips")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📄 Paper Recommendations:**
        - Heavy paper (200-300gsm)
        - Smooth or lightly textured
        - White or cream colored
        - A4 or Letter size
        """)
    
    with col2:
        st.markdown("""
        **🖊️ Coloring Tools:**
        - Colored pencils
        - Fine-tip markers
        - Gel pens
        - Watercolor pencils
        """)
    
    with col3:
        st.markdown("""
        **⚙️ Print Settings:**
        - Highest quality mode
        - 300 DPI or higher
        - No scaling/fit to page
        - Black ink only
        """)

def create_mandala_prompt(word, complexity, style):
    """Create a detailed prompt for Mandala generation"""
    
    # Base prompt structure
    base_prompt = f"""Create a beautiful, symmetrical Mandala artwork inspired by the word '{word}'. 
    The design should be in black and white line art style, perfect for coloring books."""
    
    # Complexity variations
    complexity_prompts = {
        "Simple": "Use clean, simple geometric patterns with wide spaces for easy coloring. Minimal detail, bold lines.",
        "Moderate": "Include moderate detail with traditional mandala elements like circles, petals, and geometric shapes.",
        "Detailed": "Create intricate patterns with fine details, multiple layers, and complex geometric arrangements.",
        "Very Detailed": "Design an extremely detailed mandala with very fine lines, multiple concentric circles, and elaborate patterns."
    }
    
    # Style variations
    style_prompts = {
        "Traditional Mandala": "Follow traditional Sanskrit mandala design principles with circular symmetry, lotus petals, and sacred geometry.",
        "Geometric Patterns": "Focus on geometric shapes, mathematical patterns, triangles, hexagons, and angular designs.",
        "Nature-Inspired": "Incorporate natural elements like flowers, leaves, vines, and organic flowing patterns.",
        "Abstract Designs": "Create abstract, flowing patterns with curved lines and artistic interpretations."
    }
    
    # Technical specifications
    technical_specs = """
    IMPORTANT: The artwork must be:
    - Pure black lines on white background
    - High contrast for clear printing
    - Perfectly symmetrical (8-fold or 12-fold radial symmetry)
    - No shading, gradients, or gray tones
    - Clean, printable line art style
    - Suitable for coloring with pens, pencils, or markers
    """
    
    # Combine all elements
    full_prompt = f"{base_prompt} {complexity_prompts[complexity]} {style_prompts[style]} {technical_specs}"
    
    return full_prompt

if __name__ == "__main__":
    main()