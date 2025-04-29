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
            You are an expert security analyst specializing in retail theft detection. Your role is to craft detailed prompts that will enable the CV model to detect shoplifting activities with high precision. Focus on specific behavioral patterns and physical actions that indicate theft.

            Key Areas to Monitor:

            1. Hand Movements and Item Handling:
               - Quick grabbing motions
               - Transferring items to pockets, sleeves, or waistband
               - Concealing items behind other products
               - Removing security tags or packaging
               - Hand movements near clothing or personal bags

            2. Body Language and Positioning:
               - Using body to block camera views
               - Unusual posture or stance while handling items
               - Looking around frequently while handling merchandise
               - Position relative to shelves and displays
               - Crouching or reaching into unusual areas

            3. Concealment Locations:
               - Pockets (front, back, inside jacket)
               - Personal bags or backpacks
               - Loose or baggy clothing
               - Under arms or in sleeves
               - Between or under other items

            4. Suspicious Patterns:
               - Multiple trips to the same area
               - Selecting items without examining them
               - Moving to blind spots or less visible areas
               - Waiting for other customers to leave
               - Coordinated actions with other individuals

            5. Pre-theft Indicators:
               - Examining security cameras or staff locations
               - Testing store security measures
               - Distracting or separating from staff
               - Creating diversions
               - Unusual entry/exit patterns

            Your prompts should guide the CV model to:
            1. Track hand movements meticulously
            2. Note every instance of item concealment
            3. Identify suspicious body language
            4. Recognize patterns across multiple frames
            5. Consider the context of the retail environment

            Remember: Focus on objective behavioral indicators rather than personal characteristics.
            """

    def generate_prompt(self) -> str:
        # Create user message
        user_message = """
        Analyze these surveillance frames for potential shoplifting activity. Pay special attention to:

        1. Hand Movements:
           - Where are the person's hands at all times?
           - Are they placing items in pockets, clothing, or bags?
           - Do they handle merchandise in unusual ways?
           - Are there quick or concealed movements?

        2. Item Tracking:
           - What happens to each item they pick up?
           - Do items disappear from view?
           - Are items hidden behind others?
           - Is there any tampering with packaging or tags?

        3. Concealment Behavior:
           - Check all pockets and clothing for bulges or changes
           - Monitor personal bags and their contents
           - Watch for items being hidden in carried objects
           - Note any unusual body positions while handling items

        4. Behavioral Patterns:
           - Are they checking for staff or cameras?
           - Do they move to less visible areas?
           - Is their behavior consistent with normal shopping?
           - Are there multiple people working together?

        Provide detailed observations about:
        - Exact hand movements and item locations
        - Specific concealment methods used
        - Changes in clothing or bag appearance
        - Sequence of suspicious actions
        - Any attempts to avoid detection

        Follow the chain-of-thought method to break down each observation into specific, actionable details.
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
            1. Each person's hand movements and item handling
            2. Any items being placed in pockets, clothing, or bags
            3. Suspicious concealment attempts or movements
            4. Changes in clothing or bag appearance
            5. Behavioral patterns indicating theft

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
            You are an expert retail security analyst reviewing surveillance frames to detect shoplifting activities.
            Your analysis must be thorough and accurate, with special attention to concealment actions that may be
            partially obscured or happen quickly. Pay close attention to any item movements near bags, pockets, or clothing.

            Normal Shopping Behaviors (Not suspicious on their own):
            1. Picking up and examining items openly
            2. Holding items visibly while shopping
            3. Putting items back on shelves in plain view
            4. Looking at product details or prices
            5. Comparing different items openly
            6. Using shopping baskets/carts properly
            7. Showing items to companions openly
            8. Moving between sections with items visible
            9. Normal adjustment of clothing without items
            10. Using fitting rooms with staff knowledge

            CRITICAL: Concealment Indicators (ANY of these should trigger high alert):
            1. Direct Item Concealment:
               - ANY movement of items into pockets, even partially visible
               - ANY placement of items into personal bags/backpacks
               - ANY concealment under or inside clothing
               - Items disappearing from view near body/bags
               - Quick movements of hands with items near concealment areas
               - Even BRIEF or PARTIAL view of concealment action is significant

            2. High-Risk Behaviors (Support concealment determination):
               - Taking items behind displays/obstacles
               - Turning back to camera while handling items
               - Quick or furtive movements with merchandise
               - Looking around while handling items
               - Moving to less visible areas with items
               - Adjusting clothing/bags after handling items
               - Separating from shopping companions during concealment

            3. Post-Handling Indicators:
               - Items no longer visible after handling
               - Empty hands after item was present
               - Bulges in clothing/bags where none existed
               - Avoiding areas where concealment occurred
               - Changes in movement/behavior after handling
               - Leaving area quickly after handling items

            When analyzing each batch, you MUST:
            - Watch for ANY item disappearance, even briefly
            - Note ALL movements near pockets/bags/clothing
            - Track items through ENTIRE sequence
            - Pay special attention to quick movements
            - Notice changes in item visibility
            - Look for concealment even if partially obscured

            Output Format Requirements:

            ### Summary of Current Batch:
            - Note ALL item handling
            - Describe ANY concealment actions
            - Track item visibility
            - Document behavioral patterns

            ### Connection to Previous Analysis:
            - Track items across batches
            - Note behavior patterns
            - Connect related actions
            - Follow item movements

            ### Shoplifting Determination: Yes / No
            Determine "Yes" if ANY of these are observed:
            - ANY item goes into pocket/bag/clothing
            - Items disappear near body/bags
            - Clear concealment movement, even if partially obscured
            - Quick movements followed by item disappearance
            
            Determine "No" ONLY if:
            - ALL items remain fully visible
            - NO concealment movements observed
            - ALL item handling is clearly legitimate

            ### Confidence Level: XX%
            - 90%+ for clear concealment, even if brief
            - 80-89% for partially obscured concealment
            - 70-79% for suspicious movements with item disappearance
            - 50-69% for suspicious behavior without clear concealment
            - <50% for clearly legitimate shopping

            ### Key Behaviors Supporting Conclusion:
            - Document ANY concealment actions
            - Note item disappearances
            - Describe suspicious movements
            - Track item visibility

            Remember:
            1. Even PARTIAL concealment view is significant
            2. Quick movements can indicate concealment
            3. Items disappearing near body/bags is suspicious
            4. Watch for turning away from camera
            5. Track items through entire sequence
            6. Brief concealment is still concealment
            7. Being partially obscured doesn't negate clear concealment
            8. Be precise with confidence levels based on evidence quality
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

        # Add reminder about required format for small batches
        if len(frames_data) < BATCH_SIZE:
            format_reminder = """
            IMPORTANT: Even for small batches, you must follow this exact format:

            ### Summary of Current Batch:
            [Your summary here]

            ### Shoplifting Determination: [Yes/No]

            ### Confidence Level: [XX%]

            ### Key Behaviors Supporting Conclusion:
            - [Behavior 1]
            - [Behavior 2]
            etc.
            """
            user_content.append({"type": "text", "text": format_reminder})

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
            analysis = response.choices[0].message.content

            # Verify and fix format if necessary
            if not analysis.strip().startswith("###"):
                analysis = self.ensure_proper_format(analysis)

            return analysis
        except Exception as e:
            self.logger.error(f"Error getting analysis: {str(e)}")
            return f"Error: {str(e)}"

    def ensure_proper_format(self, analysis: str) -> str:
        """
        Ensure the analysis follows the proper format with all required sections.
        """
        # If analysis already starts with ###, return as is
        if analysis.strip().startswith("###"):
            return analysis

        # Extract key information from unformatted analysis
        lines = analysis.strip().split("\n")
        determination = "No"
        confidence = "50%"
        behaviors = []
        summary = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "shoplifting" in line.lower() and any(word in line.lower() for word in ["is", "appears", "seems"]):
                determination = "Yes" if any(word in line.lower() for word in ["is", "confirmed", "clear"]) else "No"
            elif "confidence" in line.lower() and "%" in line:
                confidence = line.split("%")[0].split()[-1] + "%"
            elif line.startswith("-") or line.startswith("*"):
                behaviors.append(line.strip("- *").strip())
            else:
                summary.append(line)

        # Format the analysis properly
        formatted_analysis = f"""
### Summary of Current Batch:
{' '.join(summary)}

### Shoplifting Determination: {determination}

### Confidence Level: {confidence}

### Key Behaviors Supporting Conclusion:
"""
        for behavior in behaviors:
            formatted_analysis += f"- {behavior}\n"

        return formatted_analysis.strip()


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
            confidence_str = result.get("confidence_level", "0%")
            confidence_str = confidence_str.replace("*", "").replace("%", "").strip()
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
        Combine multiple batch results into a final analysis, giving more weight to later batches
        and considering the persistence of suspicious behaviors.
        """
        if not batch_results:
            return None
            
        total_confidence = 0
        weighted_confidence_sum = 0
        total_weight = 0
        suspicious_behaviors_count = 0
        
        # Get video name from the first batch result
        video_name = batch_results[0].get("sequence_name", "unknown_sequence")
        
        # Track suspicious behaviors across batches
        all_behaviors = set()
        
        # Calculate weighted confidence and determination
        for idx, result in enumerate(batch_results):
            weight = idx + 1  # Later batches get higher weights
            
            # Extract confidence percentage, handling asterisk format and empty values
            confidence_str = result.get("confidence_level", "0%")
            if not confidence_str.strip():  # Handle completely empty strings
                confidence_str = "0%"
                self.logger.warning(f"Empty confidence value in batch {idx + 1}, using 0%")
            
            confidence_str = confidence_str.replace("*", "").replace("%", "").strip()
            try:
                confidence = float(confidence_str)
            except (ValueError, TypeError):
                confidence = 0
                self.logger.warning(f"Invalid confidence value in batch {idx + 1}: {confidence_str}")
            
            # Weight the confidence
            weighted_confidence = confidence * weight
            weighted_confidence_sum += weighted_confidence
            
            # Track suspicious behaviors
            behaviors = result.get("key_behaviors", [])
            all_behaviors.update(behaviors)
            
            # Count weighted shoplifting determinations, handling asterisk format and empty values
            determination = result.get("shoplifting_determination", "").lower()
            if not determination.strip():  # Handle completely empty strings
                determination = "no"
                self.logger.warning(f"Empty shoplifting determination in batch {idx + 1}, using 'no'")
            
            determination = determination.replace("*", "").strip()
            confidence_weight = confidence / 100.0  # Convert confidence to 0-1 scale
            
            # If this batch shows suspicious behavior, increase its weight
            behavior_multiplier = 1.0
            suspicious_keywords = ["conceal", "avoid", "nervous", "suspicious", "security tag", 
                                "personal bag", "backpack", "hiding", "steal"]
            
            for behavior in behaviors:
                if any(keyword in behavior.lower() for keyword in suspicious_keywords):
                    suspicious_behaviors_count += 1
                    behavior_multiplier = 1.5  # Increase weight for suspicious behaviors
                    break
            
            if determination == "yes":
                total_confidence += weight * confidence_weight * behavior_multiplier
            elif determination == "no":
                total_confidence -= weight * confidence_weight
            else:
                self.logger.warning(f"Invalid shoplifting determination in batch {idx + 1}: {determination}")
            
            total_weight += weight
        
        # Calculate final metrics
        avg_confidence = weighted_confidence_sum / total_weight if total_weight > 0 else 0
        
        # Normalize total_confidence to [-1, 1] range and then to [0, 1] for probability
        normalized_confidence = total_confidence / total_weight if total_weight > 0 else 0
        
        # Adjust probability based on suspicious behavior patterns
        behavior_adjustment = min(suspicious_behaviors_count * 0.1, 0.3)  # Cap adjustment at 0.3
        shoplifting_probability = ((normalized_confidence + 1) / 2) + behavior_adjustment
        
        # Ensure probability stays in [0, 1] range
        shoplifting_probability = max(0, min(1, shoplifting_probability))
        
        # Create final determination based on probability and behavior patterns
        # Lower the threshold if we see consistent suspicious behaviors
        threshold = 0.45 if suspicious_behaviors_count >= 2 else 0.5
        final_determination = "Yes" if shoplifting_probability > threshold else "No"
        
        # Generate model-based summary
        total_summary = self.generate_sequence_summary(batch_results)
        
        return {
            "sequence_name": video_name,
            "total_batches_analyzed": len(batch_results),
            "shoplifting_determination": final_determination,
            "confidence_level": f"{avg_confidence:.1f}%",
            "shoplifting_probability": f"{shoplifting_probability:.2f}",
            "suspicious_behaviors_found": suspicious_behaviors_count,
            "total_summary": total_summary,
            "batch_results": batch_results
        }
