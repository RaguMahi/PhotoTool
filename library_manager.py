import os
from datetime import datetime
from models import ImageLibrary, TemplateLibrary, JobTemplate, get_db
import json

class LibraryManager:
    def __init__(self):
        self.image_dir = "stored_images"
        self.template_dir = "stored_templates"
        self.job_dir = "stored_jobs"
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.job_dir, exist_ok=True)

    def save_image(self, image, name, category, processing_params):
        """Save an image to the library with metadata"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.png"
        file_path = os.path.join(self.image_dir, filename)

        # Save the image file
        image.save(file_path)

        # Save metadata to database
        db = next(get_db())
        try:
            image_entry = ImageLibrary(
                name=name,
                category=category,
                file_path=file_path,
                processing_params=processing_params
            )
            db.add(image_entry)
            db.commit()
            return image_entry
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def save_template(self, template_image, name, description=None, default_params=None):
        """Save a template to the library"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.png"
        file_path = os.path.join(self.template_dir, filename)

        # Save the template file
        template_image.save(file_path)

        # Save metadata to database
        db = next(get_db())
        try:
            template_entry = TemplateLibrary(
                name=name,
                description=description,
                file_path=file_path,
                default_params=default_params or {}
            )
            db.add(template_entry)
            db.commit()
            return template_entry
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def save_job(self, name, template_id, screenshot, alignment_params):
        """Save a job template with screenshot and alignment settings"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_job_{name}.png"
        file_path = os.path.join(self.job_dir, filename)

        # Save the screenshot file
        screenshot.save(file_path)

        # Save job metadata to database
        db = next(get_db())
        try:
            job_entry = JobTemplate(
                name=name,
                template_id=template_id,
                screenshot_path=file_path,
                alignment_params=alignment_params
            )
            db.add(job_entry)
            db.commit()
            return job_entry
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_images(self):
        """Get all images from the library"""
        db = next(get_db())
        try:
            return db.query(ImageLibrary).order_by(ImageLibrary.created_at.desc()).all()
        finally:
            db.close()

    def get_templates(self):
        """Get all templates from the library"""
        db = next(get_db())
        try:
            return db.query(TemplateLibrary).order_by(TemplateLibrary.created_at.desc()).all()
        finally:
            db.close()

    def get_jobs(self):
        """Get all job templates"""
        db = next(get_db())
        try:
            return db.query(JobTemplate).order_by(JobTemplate.created_at.desc()).all()
        finally:
            db.close()

    def get_template_by_id(self, template_id):
        """Get a template by its ID"""
        db = next(get_db())
        try:
            return db.query(TemplateLibrary).filter(TemplateLibrary.id == template_id).first()
        finally:
            db.close()

    def delete_image(self, image_id):
        """Delete an image from the library"""
        db = next(get_db())
        try:
            image = db.query(ImageLibrary).filter(ImageLibrary.id == image_id).first()
            if image and os.path.exists(image.file_path):
                os.remove(image.file_path)
            db.delete(image)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def delete_template(self, template_id):
        """Delete a template from the library"""
        db = next(get_db())
        try:
            template = db.query(TemplateLibrary).filter(TemplateLibrary.id == template_id).first()
            if template and os.path.exists(template.file_path):
                os.remove(template.file_path)
            db.delete(template)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def delete_templates(self, template_ids):
        """Delete multiple templates from the library"""
        db = next(get_db())
        try:
            templates = db.query(TemplateLibrary).filter(TemplateLibrary.id.in_(template_ids)).all()
            for template in templates:
                if template and os.path.exists(template.file_path):
                    os.remove(template.file_path)
                db.delete(template)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_job_by_id(self, job_id):
        """Get a job template by its ID"""
        db = next(get_db())
        try:
            return db.query(JobTemplate).filter(JobTemplate.id == job_id).first()
        finally:
            db.close()

    def save_batch(self, batch_name, job_id, processed_images):
        """Save a batch of processed images
        Args:
            batch_name (str): Name for this batch of processed images
            job_id (int): ID of the job template used
            processed_images (list): List of tuples containing (original_name, processed_image)
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        batch_dir = os.path.join(self.job_dir, f"batch_{timestamp}_{batch_name}")
        os.makedirs(batch_dir, exist_ok=True)

        saved_images = []
        for original_name, processed_image in processed_images:
            # Save processed image
            filename = f"{timestamp}_{original_name}"
            file_path = os.path.join(batch_dir, filename)
            processed_image.save(file_path)
            saved_images.append(file_path)

        # We could add a new BatchLibrary model to track batches in the database
        # For now, we'll just save the images in an organized directory structure
        return saved_images