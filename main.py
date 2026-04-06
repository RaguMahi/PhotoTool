import streamlit as st
import numpy as np
from PIL import Image
import cv2
from image_processor import ImageProcessor
from utils import get_image_info, convert_to_pil, convert_to_cv2
import io
from library_manager import LibraryManager
from models import init_db
import json
import os
from datetime import datetime
import zipfile  # Add zipfile import for batch downloads

def show_homepage():
    st.title("🖼️ Image Enhancement Studio Bolt")
    st.write("Welcome to the Image Enhancement Studio! Choose a section to begin:")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        if st.button("📸 Image Editor", use_container_width=True):
            st.session_state.page = "editor"
            st.rerun()
        st.write("Upload and enhance your images with professional tools")

    with col2:
        if st.button("🗂️ Image Library", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()
        st.write("Browse and manage your enhanced images")

    with col3:
        if st.button("📱 Add Template Image", use_container_width=True):
            st.session_state.page = "merge"
            st.rerun()
        st.write("Add new phone templates to your collection")

    with col4:
        if st.button("📱 Template Library", use_container_width=True):
            st.session_state.page = "templates"
            st.rerun()
        st.write("Manage your phone templates collection")

    with col5:
        if st.button("📋 Jobs Library", use_container_width=True):
            st.session_state.page = "jobs"
            st.rerun()
        st.write("View and manage your merge jobs")

    with col6:
        if st.button("🔄 Batch Jobs", use_container_width=True):
            st.session_state.page = "batch_jobs"
            st.rerun()
        st.write("View processed batch jobs")

def show_image_merge():
    st.title("📱 Add Template Image")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("Upload a phone template to add it to your template library")

    # Template upload section
    template = st.file_uploader("Upload Phone Template", type=['png', 'jpg', 'jpeg'], key="phone_template")

    if template:
        template_img = Image.open(template)

        # Template save section - Moved above the image display
        st.subheader("Save Template to Library")
        template_name = st.text_input("Template Name")
        template_desc = st.text_area("Template Description (optional)")

        if st.button("Save Template"):
            try:
                library_manager.save_template(
                    template_img,
                    template_name,
                    template_desc,
                    default_params={
                        'scale_factor': 0.8,  # Default values
                        'x_offset': 0,
                        'y_offset': 0
                    }
                )
                st.success("Template saved successfully!")
            except Exception as e:
                st.error(f"Error saving template: {str(e)}")

        # Display template - Moved below the save options
        st.subheader("Phone Template Preview")
        st.image(template_img, use_container_width=True)

def show_editor():
    st.title("📸 Image Editor")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("Upload, enhance, and manipulate your images with ease!")

    # Initialize session state
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    if 'original_image' not in st.session_state:
        st.session_state.original_image = None
    if 'current_params' not in st.session_state:
        st.session_state.current_params = {}

    # Check if we're editing an existing image
    if hasattr(st.session_state, 'edit_image_path'):
        image = Image.open(st.session_state.edit_image_path)
        st.session_state.original_image = image.copy()
        st.session_state.processed_image = image.copy()
        st.session_state.current_params = st.session_state.edit_image_params

        # Clear the edit state after loading
        del st.session_state.edit_image_path
        del st.session_state.edit_image_params
    else:
        # File uploader for new images
        uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload a JPG or PNG image"
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.session_state.original_image = image.copy()
            st.session_state.processed_image = image.copy()

    if st.session_state.original_image is not None:
        # Display image information
        st.sidebar.subheader("Image Information")
        info = get_image_info(st.session_state.original_image)
        for key, value in info.items():
            st.sidebar.text(f"{key}: {value}")

        # Image processing options
        st.sidebar.subheader("Enhancement Options")

        # Basic adjustments
        brightness = st.sidebar.slider("Brightness", -100, 100, 
                                    st.session_state.current_params.get('brightness', 0))
        contrast = st.sidebar.slider("Contrast", -100, 100, 
                                   st.session_state.current_params.get('contrast', 0))
        sharpness = st.sidebar.slider("Sharpness", -100, 100, 
                                    st.session_state.current_params.get('sharpness', 0))

        # Add rotation controls above images
        st.subheader("Rotation Controls")
        rot_col1, rot_col2, rot_col3, rot_col4 = st.columns(4)

        # Initialize rotation in session state if not present
        if 'rotation_angle' not in st.session_state:
            st.session_state.rotation_angle = 0

        # Rotation buttons
        if rot_col1.button("↺ 90° CCW"):
            st.session_state.rotation_angle = (st.session_state.rotation_angle - 90) % 360
        if rot_col2.button("↺ 180° CCW"):
            st.session_state.rotation_angle = (st.session_state.rotation_angle - 180) % 360
        if rot_col3.button("↻ 90° CW"):
            st.session_state.rotation_angle = (st.session_state.rotation_angle + 90) % 360
        if rot_col4.button("↻ 180° CW"):
            st.session_state.rotation_angle = (st.session_state.rotation_angle + 180) % 360

        # Display current rotation
        st.caption(f"Current rotation: {st.session_state.rotation_angle}°")

        # Create two columns for before/after comparison
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Image")
            # Apply rotation to original image
            rotated_original = ImageProcessor().rotate_image(st.session_state.original_image, st.session_state.rotation_angle)
            st.image(rotated_original, use_container_width=True)

        # Color adjustments
        st.sidebar.subheader("Color Balance")
        red = st.sidebar.slider("Red", -100, 100, 
                              st.session_state.current_params.get('red', 0))
        green = st.sidebar.slider("Green", -100, 100, 
                                st.session_state.current_params.get('green', 0))
        blue = st.sidebar.slider("Blue", -100, 100, 
                               st.session_state.current_params.get('blue', 0))

        # Update current parameters
        st.session_state.current_params = {
            'brightness': brightness,
            'contrast': contrast,
            'sharpness': sharpness,
            'rotation': st.session_state.rotation_angle,  # Use the rotation from session state
            'red': red,
            'green': green,
            'blue': blue
        }

        # Process image with all adjustments
        processor = ImageProcessor()
        processed = processor.process_image(
            st.session_state.original_image,
            **st.session_state.current_params
        )

        st.session_state.processed_image = processed

        with col2:
            st.subheader("Processed Image")
            st.image(st.session_state.processed_image, use_container_width=True)

        # Save to library section
        st.sidebar.subheader("Save to Library")
        save_name = st.sidebar.text_input("Image Name")
        save_category = st.sidebar.text_input("Category", value="General")

        if st.sidebar.button("Save to Library"):
            try:
                library_manager.save_image(
                    st.session_state.processed_image,
                    save_name,
                    save_category,
                    st.session_state.current_params
                )
                st.sidebar.success("Image saved to library!")
            except Exception as e:
                st.sidebar.error(f"Error saving image: {str(e)}")

def show_library():
    st.title("🗂️ Image Library")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("Browse and manage your enhanced images")

    # Display saved images
    images = library_manager.get_images()

    if not images:
        st.info("No images in the library yet. Process and save some images!")
    else:
        # Create table header
        cols = st.columns([3, 2, 2])
        cols[0].markdown("**Image Name**")
        cols[1].markdown("**Date Created**")
        cols[2].markdown("**Actions**")

        st.divider()

        # Display images in table format
        for image in images:
            try:
                cols = st.columns([3, 2, 2])

                # Image Name
                cols[0].write(image.name)

                # Date Created
                date_str = image.created_at.strftime('%d/%m/%Y')
                cols[1].write(date_str)

                # Actions
                action_cols = cols[2].columns(2)

                # Preview button
                if action_cols[0].button("Preview", key=f"preview_{image.id}"):
                    saved_image = Image.open(image.file_path)
                    st.image(saved_image, caption=image.name, use_column_width=True)
                    with st.expander("Processing Parameters"):
                        st.json(image.processing_params)

                # Edit button - load image into editor
                if action_cols[1].button("Edit", key=f"edit_{image.id}"):
                    # Store image path and parameters in session state
                    st.session_state.edit_image_path = image.file_path
                    st.session_state.edit_image_params = image.processing_params
                    st.session_state.page = "editor"
                    st.rerun()

                st.divider()

            except Exception as e:
                st.error(f"Error loading image: {str(e)}")

def show_template_library():
    st.title("📱 Template Library")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("Browse and manage your phone templates")

    # Initialize preview states in session state if not present
    if 'template_previews' not in st.session_state:
        st.session_state.template_previews = {}

    # Initialize template selections in session state
    if 'selected_templates' not in st.session_state:
        st.session_state.selected_templates = set()

    # Display saved templates
    templates = library_manager.get_templates()

    if not templates:
        st.info("No templates in the library yet. Upload some templates in the Add Template Image section!")
    else:
        # Create two columns for the controls
        control_col1, control_col2 = st.columns([1, 2])

        # Select all checkbox in first column
        with control_col1:
            select_all = st.checkbox("Select All Templates", key="select_all")
            if select_all:
                st.session_state.selected_templates = set(template.id for template in templates)
            elif not select_all and len(st.session_state.selected_templates) == len(templates):
                st.session_state.selected_templates.clear()

        # Delete button in second column
        with control_col2:
            if st.session_state.selected_templates:
                if st.button("🗑️ Delete Selected Templates", type="primary", use_container_width=True):
                    try:
                        library_manager.delete_templates(list(st.session_state.selected_templates))
                        st.success(f"Successfully deleted {len(st.session_state.selected_templates)} templates")
                        st.session_state.selected_templates.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting templates: {str(e)}")

        # Create table header with removed Description column
        cols = st.columns([0.5, 3, 2, 3, 3])  # Added column for checkbox
        cols[0].write("&nbsp;")  # Empty header for checkbox column with non-breaking space
        cols[1].write("<p style='font-weight: bold; margin: 0;'>Template Name</p>", unsafe_allow_html=True)
        cols[2].write("<p style='font-weight: bold; margin: 0;'>Date Added</p>", unsafe_allow_html=True)
        cols[3].write("<p style='font-weight: bold; margin: 0;'>Preview</p>", unsafe_allow_html=True)
        cols[4].write("<p style='font-weight: bold; margin: 0;'>Actions</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 0; margin-bottom: 10px;'>", unsafe_allow_html=True)  # Custom styled divider

        # Display templates in table format
        for template in templates:
            try:
                cols = st.columns([0.5, 3, 2, 3, 3])  # Matching column widths from header

                # Selection checkbox
                if cols[0].checkbox("", key=f"select_{template.id}", 
                                  value=template.id in st.session_state.selected_templates):
                    if template.id not in st.session_state.selected_templates:
                        st.session_state.selected_templates.add(template.id)
                        st.rerun()
                else:
                    if template.id in st.session_state.selected_templates:
                        st.session_state.selected_templates.discard(template.id)
                        st.rerun()

                # Template Name
                cols[1].write(template.name)

                # Date Added
                date_str = template.created_at.strftime('%d/%m/%Y')
                cols[2].write(date_str)

                # Preview button - made wider with toggle functionality
                preview_key = f"preview_{template.id}"
                if cols[3].button(
                    "📷 " + ("Hide Preview" if st.session_state.template_previews.get(preview_key, False) else "Show Preview"),
                    key=preview_key,
                    use_container_width=True
                ):
                    # Toggle preview state
                    st.session_state.template_previews[preview_key] = not st.session_state.template_previews.get(preview_key, False)
                    st.rerun()

                # Show preview if enabled
                if st.session_state.template_previews.get(preview_key, False):
                    template_img = Image.open(template.file_path)
                    st.image(template_img, caption=template.name, use_container_width=True)
                    if template.description:  # Show description only in preview
                        st.write(f"Description: {template.description}")
                    with st.expander("Default Parameters"):
                        st.json(template.default_params)

                # Create Job button - made wider with non-wrapping text
                if cols[4].button(
                    "➕ Create Job",
                    key=f"create_job_{template.id}",
                    use_container_width=True,
                    help="Create a new job using this template"
                ):
                    st.session_state.selected_template_id = template.id
                    st.session_state.page = "create_job"
                    st.rerun()

                st.divider()

            except Exception as e:
                st.error(f"Error loading template: {str(e)}")

def show_create_job():
    st.title("📱 Create New Job")
    if st.button("← Back to Templates"):
        st.session_state.page = "templates"
        st.rerun()

    # Get the selected template
    template = library_manager.get_template_by_id(st.session_state.selected_template_id)
    if not template:
        st.error("Template not found!")
        return

    # Job name input
    job_name = st.text_input("Job Name", help="Enter a name for this job")

    # Screenshot upload
    st.subheader("Upload App Screenshot")
    screenshot = st.file_uploader("Choose screenshot", type=['png', 'jpg', 'jpeg'])

    if screenshot:
        screenshot_img = Image.open(screenshot)
        template_img = Image.open(template.file_path)  # Load template image but don't display it

        # Alignment controls
        st.subheader("Alignment Settings")

        # Scale factor controls
        scale_col1, scale_col2 = st.columns([3, 1])
        with scale_col1:
            scale_factor = st.slider("Screenshot Scale", 0.1, 1.0, 0.8, 0.01)
        with scale_col2:
            scale_input = st.number_input("Scale Value", 
                                      min_value=0.1, 
                                      max_value=1.0, 
                                      value=scale_factor,
                                      step=0.01)
            if scale_input != scale_factor:
                scale_factor = scale_input

        # Position controls
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            x_offset = st.slider("Horizontal Position", -100, 100, 0, 1)
        with h_col2:
            x_input = st.number_input("H-Position Value", 
                                  min_value=-100, 
                                  max_value=100, 
                                  value=x_offset,
                                  step=1)
            if x_input != x_offset:
                x_offset = x_input

        v_col1, v_col2 = st.columns([3, 1])
        with v_col1:
            y_offset = st.slider("Vertical Position", -100, 100, 0, 1)
        with v_col2:
            y_input = st.number_input("V-Position Value", 
                                  min_value=-100, 
                                  max_value=100, 
                                  value=y_offset,
                                  step=1)
            if y_input != y_offset:
                y_offset = y_input

        # Preview merged result
        st.subheader("Preview")
        processor = ImageProcessor()
        merged_image = processor.merge_app_screenshot(
            template_img,
            screenshot_img,
            scale_factor=scale_factor,
            x_offset=x_offset,
            y_offset=y_offset
        )
        st.image(merged_image, caption="Merged Preview", use_container_width=True)

        # Save job button
        if st.button("Save Job"):
            try:
                if not job_name:
                    st.error("Please enter a job name")
                    return

                library_manager.save_job(
                    job_name,
                    template.id,
                    screenshot_img,
                    {
                        'scale_factor': scale_factor,
                        'x_offset': x_offset,
                        'y_offset': y_offset
                    }
                )
                st.success("Job saved successfully!")
                st.session_state.page = "templates"
                st.rerun()
            except Exception as e:
                st.error(f"Error saving job: {str(e)}")

def show_jobs_library():
    st.title("📋 Jobs Library")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("Browse and manage your saved merge jobs")

    # Initialize preview states in session state if not present
    if 'job_previews' not in st.session_state:
        st.session_state.job_previews = {}

    # Display saved jobs
    jobs = library_manager.get_jobs()

    if not jobs:
        st.info("No jobs in the library yet. Create some jobs from the Template Library!")
    else:
        # Create table header with wider preview column
        cols = st.columns([3, 2, 2, 3, 1])  # Added new column for batch processing
        cols[0].markdown("**Job Name**")
        cols[1].markdown("**Date Created**")
        cols[2].markdown("**Template**")
        cols[3].markdown("**Preview**")
        cols[4].markdown("**Actions**")

        st.divider()

        # Display jobs in table format
        for job in jobs:
            try:
                cols = st.columns([3, 2, 2, 3, 1])  # Matching header column widths
                # Job Name
                cols[0].write(job.name)

                # Date Created
                date_str = job.created_at.strftime('%d/%m/%Y')
                cols[1].write(date_str)

                # Template Info
                template = library_manager.get_template_by_id(job.template_id)
                cols[2].write(template.name if template else "Template not found")

                # Preview toggle button
                preview_key = f"preview_job_{job.id}"
                if cols[3].button(
                    "📷 " + ("Hide Preview" if st.session_state.job_previews.get(preview_key, False) else "Show Preview"),
                    key=preview_key,
                    use_container_width=True
                ):
                    st.session_state.job_previews[preview_key] = not st.session_state.job_previews.get(preview_key, False)
                    st.rerun()

                # Process Batch button
                action_cols = cols[4].columns(1)
                if action_cols[0].button(
                    "🔄 Process Batch",
                    key=f"process_batch_{job.id}",
                    use_container_width=True,
                    help="Process multiple images using this job's settings"
                ):
                    st.session_state.selected_job_id = job.id
                    st.session_state.page = "process_batch"
                    st.rerun()

                # Show preview and parameters if enabled
                if st.session_state.job_previews.get(preview_key, False):
                    # Show parameters in collapsed expander above the preview
                    with st.expander("Job Adjustment Settings", expanded=False):
                        st.write("Scale Factor:", job.alignment_params.get('scale_factor', 0.8))
                        st.write("Horizontal Position:", job.alignment_params.get('x_offset', 0))
                        st.write("Vertical Position:", job.alignment_params.get('y_offset', 0))

                    # Load and display the preview
                    template_img = Image.open(template.file_path)
                    screenshot_img = Image.open(job.screenshot_path)

                    processor = ImageProcessor()
                    merged_preview = processor.merge_app_screenshot(
                        template_img,
                        screenshot_img,
                        **job.alignment_params
                    )

                    st.image(merged_preview, caption=f"Job: {job.name}", use_container_width=True)

            except Exception as e:
                st.error(f"Error loading job: {str(e)}")

def show_process_batch():
    st.title("🔄 Process Batch Images")
    if st.button("← Back to Jobs Library"):
        st.session_state.page = "jobs"
        st.rerun()

    # Get the selected job
    job = library_manager.get_job_by_id(st.session_state.selected_job_id)
    if not job:
        st.error("Job not found!")
        return

    template = library_manager.get_template_by_id(job.template_id)
    if not template:
        st.error("Template not found!")
        return

    # Batch name input
    batch_name = st.text_input("Batch Name", help="Enter a name for this batch of images")

    # Multi-file uploader
    uploaded_files = st.file_uploader(
        "Upload Images",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Drag and drop multiple images or click to browse"
    )

    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} images")

        if st.button("Process Batch"):
            if not batch_name:
                st.error("Please enter a batch name")
                return

            try:
                # Load template image once
                template_img = Image.open(template.file_path)
                processor = ImageProcessor()

                # Process each image
                processed_images = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, file in enumerate(uploaded_files):
                    try:
                        status_text.write(f"Processing image {i+1} of {len(uploaded_files)}...")

                        # Process image
                        input_img = Image.open(file)
                        merged_image = processor.merge_app_screenshot(
                            template_img,
                            input_img,
                            **job.alignment_params
                        )
                        processed_images.append((file.name, merged_image))

                        # Update progress
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")

                if processed_images:
                    # Save batch to library
                    library_manager.save_batch(
                        batch_name,
                        job.id,
                        processed_images
                    )
                    status_text.write("✅ Batch processing complete!")
                    st.success(f"Successfully processed {len(processed_images)} images")

                    # Show preview grid
                    st.subheader("Processed Images Preview")
                    cols = st.columns(4)
                    for idx, (name, img) in enumerate(processed_images):
                        cols[idx % 4].image(img, caption=name, use_container_width=True)
                        if (idx + 1) % 4 == 0:
                            cols = st.columns(4)

            except Exception as e:
                st.error(f"Error during batch processing: {str(e)}")

def show_batch_jobs():
    st.title("🔄 Batch Jobs Library")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.write("Browse and manage your processed batch jobs")

    # Initialize session state for selected images if not present
    if 'selected_batch_images' not in st.session_state:
        st.session_state.selected_batch_images = {}

    # Display the batch jobs from the stored_jobs directory
    batch_jobs_dir = os.path.join(library_manager.job_dir)

    if not os.path.exists(batch_jobs_dir):
        st.info("Batch jobs directory not found. Please process some batch images first.")
        return

    try:
        batch_folders = [f for f in os.listdir(batch_jobs_dir) 
                        if f.startswith('batch_') and os.path.isdir(os.path.join(batch_jobs_dir, f))]
    except Exception as e:
        st.error(f"Error accessing batch jobs directory: {str(e)}")
        return

    if not batch_folders:
        st.info("No batch jobs found. Process some batch images from the Jobs Library!")
    else:
        # Sort batch folders by creation time (newest first)
        batch_folders.sort(reverse=True, key=lambda x: os.path.getmtime(os.path.join(batch_jobs_dir, x)))

        for batch_folder in batch_folders:
            try:
                # Extract batch name for display
                batch_name = batch_folder.replace('batch_', '').split('_', 2)[2]
                with st.expander(f"📁 {batch_name}", expanded=False):
                    batch_path = os.path.join(batch_jobs_dir, batch_folder)

                    # Get creation time
                    creation_time = datetime.fromtimestamp(os.path.getctime(batch_path))
                    st.write(f"Created: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}")

                    # Get and filter image files
                    images = [f for f in os.listdir(batch_path) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

                    if not images:
                        st.info("No images found in this batch.")
                        continue

                    # Initialize selection state for this batch
                    if batch_folder not in st.session_state.selected_batch_images:
                        st.session_state.selected_batch_images[batch_folder] = set()

                    # Select all checkbox
                    select_all = st.checkbox(
                        "Select All Images", 
                        key=f"select_all_{batch_folder}",
                        value=len(st.session_state.selected_batch_images[batch_folder]) == len(images)
                    )

                    if select_all:
                        st.session_state.selected_batch_images[batch_folder] = set(images)
                    elif not select_all and len(st.session_state.selected_batch_images[batch_folder]) == len(images):
                        st.session_state.selected_batch_images[batch_folder].clear()

                    # Show total images count and download button in the same line
                    col1, col2 = st.columns([2, 2])
                    col1.write(f"Total images: {len(images)}")

                    # Show download button if images are selected
                    selected_count = len(st.session_state.selected_batch_images[batch_folder])
                    if selected_count > 0:
                        if col2.button("📥 Download Selected Images", key=f"download_{batch_folder}"):
                            # Create a ZIP file in memory
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for image_name in st.session_state.selected_batch_images[batch_folder]:
                                    image_path = os.path.join(batch_path, image_name)
                                    # Use only the original filename part for the zip
                                    zip_filename = image_name.split('_')[-1]
                                    zip_file.write(image_path, zip_filename)

                            # Prepare the ZIP file for download
                            zip_buffer.seek(0)
                            st.download_button(
                                label="Download ZIP",
                                data=zip_buffer,
                                file_name=f"{batch_name}_selected_images.zip",
                                mime="application/zip",
                                key=f"download_zip_{batch_folder}"
                            )

                    # Display images in a grid
                    cols = st.columns(4)
                    for idx, image_name in enumerate(images):
                        image_path = os.path.join(batch_path, image_name)
                        try:
                            col = cols[idx % 4]
                            # Add checkbox for image selection
                            if col.checkbox(
                                "📋",
                                key=f"select_{batch_folder}_{image_name}",
                                value=image_name in st.session_state.selected_batch_images[batch_folder]
                            ):
                                st.session_state.selected_batch_images[batch_folder].add(image_name)
                            else:
                                st.session_state.selected_batch_images[batch_folder].discard(image_name)

                            # Display image
                            img = Image.open(image_path)
                            col.image(
                                img,
                                caption=image_name.split('_')[-1],  # Show only the original filename
                                use_container_width=True
                            )

                            # Create new row after every 4 images
                            if (idx + 1) % 4 == 0 and idx < len(images) - 1:
                                cols = st.columns(4)
                        except Exception as e:
                            cols[idx % 4].error(f"Error loading image: {str(e)}")

            except Exception as e:
                st.error(f"Error processing batch folder {batch_folder}: {str(e)}")
                continue

def main():
    # Initialize database
    init_db()

    # Initialize library manager
    global library_manager
    library_manager = LibraryManager()

    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = "home"

    # Navigation
    if st.session_state.page == "home":
        show_homepage()
    elif st.session_state.page == "editor":        show_editor()
    elif st.session_state.page == "library":
        show_library()
    elif st.session_state.page == "merge":
        show_image_merge()
    elif st.session_state.page == "templates":
        show_template_library()
    elif st.session_state.page == "create_job":
        show_create_job()
    elif st.session_state.page == "jobs":
        show_jobs_library()
    elif st.session_state.page == "process_batch":
        show_process_batch()
    elif st.session_state.page == "batch_jobs":
        show_batch_jobs()

if __name__ == "__main__":
    main()