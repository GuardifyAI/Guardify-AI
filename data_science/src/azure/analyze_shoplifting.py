import os
import logging
from glob import glob
from typing import List, Optional, Dict
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from data_science.src.azure.utils import create_logger, restructure_analysis, encode_image_to_base64, load_env_variables
import base64

# Load environment variables
load_env_variables()

BATCH_SIZE = 50  # Number of frames to analyze in each batch


class PromptModel:
    def __init__(self, logger: Optional[logging.Logger] = None, system_prompt: str = None):
        """
        Initialize the PromptModel for generating prompts for CV analysis.

        Args:
            logger: Optional logger instance. If None, a default logger will be created.
        """
        # Setup logging
        if logger is None:
            self.logger = create_logger('PromptModel', 'shoplifting_analysis.log')
        else:
            self.logger = logger

        # Get Azure OpenAI credentials from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        # Check if credentials are set
        if not self.api_key or not self.endpoint:
            self.logger.error("Azure OpenAI credentials not found")
            raise ValueError(
                "Azure OpenAI credentials not found. Please set the following environment variables:\n"
                "  AZURE_OPENAI_API_KEY - Your Azure OpenAI API key\n"
                "  AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint URL\n"
                "  AZURE_OPENAI_DEPLOYMENT_NAME - Your Azure OpenAI deployment name"
            )

        # Create the endpoint URL
        if self.deployment_name and "deployments" not in self.endpoint:
            self.endpoint = f"{self.endpoint}/openai/deployments/{self.deployment_name}"

        self.logger.info("Initializing Azure OpenAI client for PromptModel")
        # Initialize the ChatCompletionsClient
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )
        self.logger.info("Azure OpenAI client initialized successfully")

        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = """
        As an assistant to the cv_model, your primary function is to help it perform its duties as a virtual security guard in a retail environment.
        Your role is to craft detailed prompts that will enable the cv_model to monitor customer behavior accurately and identify potential shoplifting activities by breaking down these complex tasks into smaller, more manageable steps.
        This approach is similar to how a human would tackle a complex problem, enhancing the cv_model's ability to process and analyze situations effectively.
        Here's how you might construct a structured prompt for the cv_model:
        Imagine you are a highly skilled security guard working at a retail store.
        Your main responsibility is to monitor customer behavior and identify potential shoplifting activities.
        Break down your observation process into the following steps:
        Initial Surveillance: Scan the store entrance and aisles.
        Look for customers who avoid eye contact with staff or surveillance cameras, or those carrying empty bags.
        Detailed Observation: Focus on individuals who exhibit unusual or suspicious movements, such as concealing items or lingering in certain areas without a clear purpose.
        Behavior Analysis: Note behaviors like repeatedly entering and exiting the store without purchases, or carrying fuller bags after visiting the store.
        Pay special attention to customers who take items and do not head towards the checkout counters, as this could indicate an intent to shoplift.
        Situation Assessment: Combine the observed details to assess whether these behaviors cumulatively suggest a potential for shoplifting.
        Reporting: Describe in detail the specific behaviors, the exact locations within the store, and articulate why these actions may suggest potential shoplifting.
        Ensure that your report is polite and professional, focusing on behavior rather than personal attributes to avoid bias and false accusations.
        Each step should guide you through the task, making it easier to process complex information and make accurate judgments.
        This structured approach will help you enhance your observational techniques, distinguishing effectively between normal customer behavior and potential security risks.
        Your prompts should be clear, instructive, and carefully designed to assist the cv_model in processing and reporting information efficiently, by breaking complex observations into smaller analytical tasks.
        Each prompt should refine the cv_model's ability to observe and evaluate with precision.
        """

    def generate_prompt(self) -> str:
        # Create user message
        user_message = """
        Generate a detailed prompt for analyzing these surveillance frames for shoplifting detection.
        The frames are in temporal sequence and show a retail environment.

        The prompt should guide the model to:
        1. Analyze each person's behavior and movements
        2. Look for suspicious interactions with merchandise
        3. Identify potential concealment attempts
        4. Note any unusual patterns or behaviors
        5. Consider the context of the retail environment

        Please provide a comprehensive prompt that will result in detailed analysis.
        The generated prompt should follow the 'chain of thought' method to break down complex tasks into smaller, more manageable steps.
        """

        # Create messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            self.logger.info("Generating prompt for CV analysis...")
            response = self.client.complete(
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            prompt = response.choices[0].message.content
            self.logger.info("Prompt generated successfully")
            return prompt
        except Exception as e:
            self.logger.error(f"Error generating prompt: {str(e)}")
            # Return a default prompt if generation fails
            return """
            Analyze these surveillance frames for potential shoplifting activity. Focus on:
            1. Each person's behavior and movements
            2. Interactions with merchandise
            3. Potential concealment attempts
            4. Unusual patterns or behaviors
            5. Context of the retail environment

            Provide detailed observations about any suspicious activities or behaviors.
            """


class CVModel:
    def __init__(self, logger: Optional[logging.Logger] = None, system_prompt: str = None):
        """
        Initialize the CVModel for analyzing video frames.

        Args:
            logger: Optional logger instance. If None, a default logger will be created.
        """
        # Setup logging
        if logger is None:
            self.logger = create_logger('CVModel', 'shoplifting_analysis.log')
        else:
            self.logger = logger

        # Get Azure OpenAI credentials from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        # Check if credentials are set
        if not self.api_key or not self.endpoint:
            self.logger.error("Azure OpenAI credentials not found")
            raise ValueError(
                "Azure OpenAI credentials not found. Please set the following environment variables:\n"
                "  AZURE_OPENAI_API_KEY - Your Azure OpenAI API key\n"
                "  AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint URL\n"
                "  AZURE_OPENAI_DEPLOYMENT_NAME - Your Azure OpenAI deployment name"
            )

        # Create the endpoint URL
        if self.deployment_name and "deployments" not in self.endpoint:
            self.endpoint = f"{self.endpoint}/openai/deployments/{self.deployment_name}"

        self.logger.info("Initializing Azure OpenAI client for CVModel")
        # Initialize the ChatCompletionsClient
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )
        self.logger.info("Azure OpenAI client initialized successfully")

        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = """
                You are a security analyst reviewing surveillance frames to determine whether shoplifting is occurring.
                You will analyze frames sequentially in batches, taking into account previous observations and conclusions.
                
                Focus on suspicious behaviors like:
                1. Concealing items in clothing, bags, or containers
                2. Removing security tags
                3. Avoiding checkout areas
                4. Displaying nervous behavior
                5. Working with accomplices to distract staff

                When analyzing each batch, consider:
                - How the current observations relate to previous findings
                - Whether suspicious behaviors are continuing or changing
                - New individuals entering the scene
                - The progression of events over time

                Strictly follow this output format using the exact section headers and structure:

                ### Summary of Current Batch:
                - Summarize behaviors in current frames using bullet points
                - Note any continuation or changes from previous observations

                ### Connection to Previous Analysis:
                - How current observations relate to previous findings
                - Whether suspicious behaviors are escalating or diminishing
                - New developments or patterns emerging

                ### Shoplifting Determination: Yes / No
                ### Confidence Level: XX%
                ### Key Behaviors Supporting Conclusion:
                - Bullet 1
                - Bullet 2
                - Bullet 3

                Make sure:
                - You always include all 5 parts of the conclusion section
                - Each part is labeled exactly as shown
                - Confidence Level must be numeric, in this format: "XX%"
                """

    def analyze_frames(self, frames_data: List[dict], prompt: str, previous_analysis: Optional[Dict] = None) -> str:
        """
        Analyze frames using the provided prompt, considering previous analysis if available.

        Args:
            frames_data: List of dictionaries containing frame data and paths
                Each dict should have:
                - 'path': The blob path of the frame
                - 'data': The frame data as bytes
            prompt: The prompt to use for analysis
            previous_analysis: Optional previous batch analysis results

        Returns:
            str: Analysis result
        """
        # Sort frames by path which should preserve temporal order
        frames_data = sorted(frames_data, key=lambda x: x['path'])

        self.logger.info(f"Analyzing {len(frames_data)} frames...")

        # Create the user message content
        user_content = [{"type": "text", "text": prompt}]

        # If we have previous analysis, add it to the prompt
        if previous_analysis:
            previous_context = f"""
            Previous Analysis Summary:
            - Determination: {previous_analysis.get('shoplifting_determination', 'Unknown')}
            - Confidence: {previous_analysis.get('confidence_level', '0%')}
            - Key Behaviors: {', '.join(previous_analysis.get('key_behaviors', []))}
            
            Please analyze the following frames in context of these previous findings.
            """
            user_content.append({"type": "text", "text": previous_context})

        # Add all frames to the user message content
        for frame in frames_data:
            # Convert frame bytes to base64 directly
            encoded_image = base64.b64encode(frame['data']).decode('utf-8')
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })

        # Create the messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Get the analysis from the model
        try:
            self.logger.info("Sending request to Azure OpenAI...")
            response = self.client.complete(
                messages=messages,
                max_tokens=4000,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error getting analysis: {str(e)}")
            return f"Error: {str(e)}"


class ShopliftingAnalyzer:
    def __init__(self):
        """Initialize the ShopliftingAnalyzer with CV and Prompt models."""
        self.logger = create_logger('ShopliftingAnalyzer', 'shoplifting_analysis.log')
        self.prompt_model = PromptModel(self.logger)
        self.cv_model = CVModel(self.logger)
        self.cached_prompt = None

    def get_prompt(self):
        if self.cached_prompt is None:
            self.cached_prompt = self.prompt_model.generate_prompt()
        return self.cached_prompt

    def analyze_batch(self, frame_data: List[dict], prompt: str, previous_analysis: Optional[Dict] = None, video_name: str = None) -> Dict[str, str]:
        """
        Analyze a batch of frames.

        Args:
            frame_data: List of dictionaries containing frame data and paths
                Each dict should have:
                - 'path': The blob path of the frame
                - 'data': The frame data as bytes
            prompt: The prompt to use for analysis
            previous_analysis: Optional previous batch analysis results
            video_name: Name of the video being analyzed

        Returns:
            Dict[str, str]: Analysis result for this batch
        """
        try:
            analysis = self.cv_model.analyze_frames(frame_data, prompt, previous_analysis)
            return restructure_analysis(analysis, video_name)
        except Exception as e:
            self.logger.error(f"Error analyzing batch for video {video_name}: {str(e)}")
            return None

    def analyze_frames_from_azure(self, video_name: str, blob_helper, frames_container: str) -> dict[str, str] | None:
        """
        Analyze frames directly from Azure blob storage.
        
        Args:
            video_name: Name of the video whose frames to analyze
            blob_helper: AzureBlobHelper instance
            frames_container: Container name where frames are stored
        """
        self.logger.info(f"=== Starting analysis of video: {video_name} from Azure storage ===")
        
        # List all frames for this video
        all_frames = sorted(blob_helper.list_blobs(frames_container, prefix=f"{video_name}/"))
        
        if not all_frames:
            self.logger.warning(f"No frames found for video {video_name}")
            return None

        self.logger.info(f"Found {len(all_frames)} frames for video: {video_name}")
            
        # Get the analysis prompt
        prompt = self.get_prompt()
        
        # Process frames in batches, keeping track of previous analysis
        batch_results = []
        previous_analysis = None
        
        for i in range(0, len(all_frames), BATCH_SIZE):
            batch_frames = all_frames[i:i + BATCH_SIZE]
            self.logger.info(f"Processing batch {i//BATCH_SIZE + 1}/{(len(all_frames) + BATCH_SIZE - 1)//BATCH_SIZE} for video: {video_name}")
            
            # Download frames for this batch
            frame_data = []
            for frame_path in batch_frames:
                frame_bytes = blob_helper.download_blob_as_bytes(frames_container, frame_path)
                frame_data.append({"path": frame_path, "data": frame_bytes})
            
            batch_result = self.analyze_batch(frame_data, prompt, previous_analysis, video_name)
            
            # Store this result for the next iteration
            if batch_result is not None:
                previous_analysis = batch_result
                batch_results.append(batch_result)
            else:
                self.logger.error(f"Failed to analyze batch for video {video_name}")
                continue
            
        # If we have no valid results, return None
        if not batch_results:
            self.logger.error(f"No valid analysis results for video {video_name}")
            return None
            
        # Combine all batch results
        final_result = self.combine_batch_results(batch_results)
        return final_result

    def analyze_all_videos(self, blob_helper, frames_container: str, results_container: str) -> List[Dict[str, str]]:
        """
        Analyze all videos with frames in Azure storage.
        
        Args:
            blob_helper: AzureBlobHelper instance
            frames_container: Container name where frames are stored
            results_container: Container name for uploading results
            
        Returns:
            List[Dict[str, str]]: List of analysis results
        """
        # Get unique video names from frames container
        all_frames = blob_helper.list_blobs(frames_container)
        video_names = set(frame_path.split('/')[0] for frame_path in all_frames if '/' in frame_path)
        
        results = []
        for video_name in video_names:
            result = self.analyze_frames_from_azure(video_name, blob_helper, frames_container)
            if result:
                # Upload result immediately
                blob_name = f"{video_name}_analysis.json"
                blob_helper.upload_json_object(results_container, blob_name, result)
                self.logger.info(f"=== Uploaded analysis for video: {video_name} ===")
                
                results.append(result)
                
        return results

    def generate_sequence_summary(self, batch_results: List[Dict[str, str]]) -> str:
        """
        Generate a comprehensive summary of the entire video sequence using the GPT model.
        """
        # Calculate the overall confidence level
        total_confidence = 0
        total_weight = 0
        for idx, result in enumerate(batch_results, 1):
            weight = idx  # Later batches get higher weights
            confidence_str = result.get("confidence_level", "0%").replace("%", "")
            try:
                confidence = float(confidence_str)
                total_confidence += confidence * weight
                total_weight += weight
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid confidence value in batch result: {confidence_str}")
        
        avg_confidence = f"{(total_confidence / total_weight if total_weight > 0 else 0):.1f}%"
        
        # Create a prompt for the model
        summary_prompt = """
        Based on the following batch analysis results, provide a concise summary of the entire video sequence.
        Focus on:
        1. Key participants and their actions
        2. Important locations and movements
        3. Notable events or behaviors
        4. Overall determination and confidence level
        
        Keep the summary clear, factual, and focused on the most important details.
        Use EXACTLY this confidence level in your summary: {confidence_level}
        
        Analysis Results:
        """.format(confidence_level=avg_confidence)
        
        # Add batch results to the prompt
        for i, result in enumerate(batch_results, 1):
            summary_prompt += f"\nBatch {i}:\n"
            summary_prompt += f"Summary: {result.get('summary_of_video', 'N/A')}\n"
        
        # Add final metrics
        summary_prompt += f"\nFinal Determination: {batch_results[-1].get('shoplifting_determination', 'N/A')}\n"
        summary_prompt += f"Overall Confidence Level: {avg_confidence}\n"
        
        # Get summary from the model
        messages = [
            {"role": "system", "content": "You are a security analysis assistant tasked with providing clear, concise summaries of surveillance footage analysis. Always use the exact confidence level provided in the prompt."},
            {"role": "user", "content": summary_prompt}
        ]
        
        try:
            response = self.cv_model.client.complete(
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return "Error generating summary"

    def combine_batch_results(self, batch_results: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Combine multiple batch results into a final analysis, giving more weight to later batches.
        """
        if not batch_results:
            return None
            
        total_confidence = 0
        weighted_yes_votes = 0
        total_weight = 0
        
        # Get video name from the first batch result
        video_name = batch_results[0].get("sequence_name", "unknown_sequence")
        
        # Give more weight to later batches
        for idx, result in enumerate(batch_results):
            weight = idx + 1  # Later batches get higher weights
            
            # Extract confidence percentage
            confidence_str = result.get("confidence_level", "0%").replace("%", "")
            try:
                confidence = float(confidence_str)
            except (ValueError, TypeError):
                confidence = 0
                self.logger.warning(f"Invalid confidence value in batch result: {confidence_str}")
            
            # Count weighted shoplifting determinations
            determination = result.get("shoplifting_determination", "").lower()
            if determination == "yes":
                weighted_yes_votes += weight
            elif determination == "no":
                weighted_yes_votes += 0  # Explicit no vote
            else:
                self.logger.warning(f"Invalid shoplifting determination in batch result: {determination}")
            
            total_confidence += confidence * weight
            total_weight += weight
        
        # Calculate final metrics
        avg_confidence = total_confidence / total_weight if total_weight > 0 else 0
        shoplifting_probability = (weighted_yes_votes / total_weight) if total_weight > 0 else 0
        
        # Create final determination
        final_determination = "Yes" if shoplifting_probability >= 0.5 else "No"
        
        # Generate model-based summary
        total_summary = self.generate_sequence_summary(batch_results)
        
        return {
            "sequence_name": video_name,
            "total_batches_analyzed": len(batch_results),
            "shoplifting_determination": final_determination,
            "confidence_level": f"{avg_confidence:.1f}%",
            "shoplifting_probability": f"{shoplifting_probability:.2f}",
            "total_summary": total_summary,
            "batch_results": batch_results
        }
