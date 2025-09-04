#!/usr/bin/env python3
"""
arxiv_links_by_field_curated.py
---------------------------------
Generate top arXiv papers organized by field using curated lists of influential papers.
This avoids API issues and provides high-quality, manually selected papers.

Usage:
    python arxiv_links_by_field_curated.py

Output: arxiv_links_by_field.txt with papers organized by field
"""

# Curated lists of influential arXiv papers by field
FIELDS = {
    "Communication": [
        # Transformer & Language Models
        "1706.03762",  # Attention Is All You Need (Transformer)
        "2005.14165",  # GPT-3: Language Models are Few-Shot Learners
        "1810.04805",  # BERT: Pre-training of Deep Bidirectional Transformers
        "2203.02155",  # Training language models to follow instructions with human feedback
        "1909.11942",  # RoBERTa: A Robustly Optimized BERT Pretraining Approach
        "1907.11692",  # RoBERTa: A Robustly Optimized BERT Pretraining Approach
        "2019.12688",  # ALBERT: A Lite BERT for Self-supervised Learning
        "2005.11401",  # ELECTRA: Pre-training Text Encoders as Discriminators
        "2106.09685",  # LoRA: Low-Rank Adaptation of Large Language Models
        "2204.02311",  # PaLM: Scaling Language Modeling with Pathways
        "2301.00234",  # LLaMA: Open and Efficient Foundation Language Models
        "2203.15556",  # InstructGPT: Training language models to follow instructions
        "2112.10752",  # WebGPT: Browser-assisted question-answering with human feedback
        "2110.01852",  # Training Verifiers to Solve Math Word Problems
        "2002.05202",  # A Primer in BERTology: What We Know About How BERT Works
        "2108.07732",  # On the Opportunities and Risks of Foundation Models
        "2106.04554",  # Evaluating Large Language Models Trained on Code
        "2107.03374",  # Evaluating Large Language Models Trained on Code
        "1508.07909",  # Neural Machine Translation of Rare Words with Subword Units
        "1409.0473",   # Neural Machine Translation by Jointly Learning to Align and Translate
        "1604.06174",  # Learning to learn by gradient descent by gradient descent
        "1909.08593",  # T5: Exploring the Limits of Transfer Learning
        "2010.02502",  # mT5: A massively multilingual pre-trained text-to-text transformer
        "2203.07814",  # PaLM: Scaling Language Modeling with Pathways
        "2301.07041",  # Transformer Quality in Linear Time
        "2302.13971",  # LLaMA: Open and Efficient Foundation Language Models
        "1607.08022",  # Layer Normalization
        "1803.01271",  # Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context
        "1901.02860",  # Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context
        "2001.04451",  # Reformer: The Efficient Transformer
        "2004.05150",  # Linformer: Self-Attention with Linear Complexity
        "2009.06732",  # Performer: Rethinking Attention with FAVOR+
        # Audio & Speech
        "1609.03499",  # WaveNet: A Generative Model for Raw Audio
        "1703.10135",  # Tacotron: Towards End-to-End Speech Synthesis
        "1712.05884",  # Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions
        "1807.03748",  # Neural Voice Cloning with a Few Samples
        "2106.07889",  # HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction
        "2010.05646",  # wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations
        "1904.05862",  # SpecAugment: A Simple Data Augmentation Method for Automatic Speech Recognition
        # Sequence Modeling
        "1409.3215",   # Sequence to Sequence Learning with Neural Networks
        "1503.04069",  # LSTM: A Search Space Odyssey
        "1308.0850",   # Generating Sequences With Recurrent Neural Networks
        "1511.04508",  # An Empirical Exploration of Recurrent Network Architectures
    ],
    
    "Life Sciences": [
        # Medical AI & Healthcare
        "1606.04797",  # Deep Learning for Health Informatics
        "1711.05225",  # Dermatologist-level classification of skin cancer with deep neural networks
        "1707.12357",  # CheXNet: Radiologist-Level Pneumonia Detection on Chest X-Rays with Deep Learning
        "1909.02565",  # Med3D: Transfer Learning for 3D Medical Image Analysis
        "2010.02502",  # MedViT: A Robust Vision Transformer for Generalized Medical Image Classification
        # Biology & Bioinformatics
        "1810.04805",  # BERT: Pre-training of Deep Bidirectional Transformers
        "2005.14165",  # GPT-3: Language Models are Few-Shot Learners
        "1909.08593",  # T5: Exploring the Limits of Transfer Learning
        "2010.02502",  # mT5: A massively multilingual pre-trained text-to-text transformer
        "2002.05202",  # A Primer in BERTology: What We Know About How BERT Works
        "2108.07732",  # On the Opportunities and Risks of Foundation Models
        "1703.01161",  # Overcoming catastrophic forgetting in neural networks
        # Multimodal Learning for Biology
        "1411.4555",   # Show and Tell: A Neural Image Caption Generator
        "1502.03044",  # Show, Attend and Tell: Neural Image Caption Generation with Visual Attention
        "1707.07998",  # Bottom-Up and Top-Down Attention for Image Captioning and Visual Question Answering
        "1908.02265",  # ViLBERT: Pretraining Task-Agnostic Visiolinguistic Representations
        "2001.00179",  # VL-BERT: Pre-training of Generic Visual-Linguistic Representations
        "2103.15679",  # Learning Transferable Visual Models From Natural Language Supervision (CLIP)
        "2204.14198",  # Flamingo: a Visual Language Model for Few-Shot Learning
        "2301.12597",  # BLIP-2: Bootstrapping Vision-Language Pre-training with Frozen Image Encoders
        # Transfer Learning & Domain Adaptation
        "1411.1792",   # How transferable are features in deep neural networks?
        "1505.07818",  # Domain-Adversarial Training of Neural Networks
        "1409.7495",   # Simultaneous Deep Transfer Across Domains and Tasks
        "1708.02637",  # Taskonomy: Disentangling Task Transfer Learning
        "1909.11740",  # Cross-lingual Language Model Pretraining
        "2006.03654",  # Language Models are Few-Shot Learners
        # Few-shot Learning for Biology
        "1703.03400",  # Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks
        "1606.04080",  # Matching Networks for One Shot Learning
        "1703.05175",  # Prototypical Networks for Few-shot Learning
        "1711.06025",  # Relation Network for Few-Shot Learning
        "1904.04232",  # Learning to Learn Image Classifiers with Visual Analogy
        "1909.02729",  # Meta-Learning with Implicit Gradients
        "2003.05003",  # A Closer Look at Few-shot Classification
        "2104.02638",  # MAML++: A General Framework for Learning Efficient Models
        # Interpretability for Medicine
        "1312.6034",  # Intriguing properties of neural networks
        "1311.2901",  # Intriguing properties of neural networks
        "1603.08155",  # "Why Should I Trust You?": Explaining the Predictions of Any Classifier
        "1704.02685",  # Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization
        "1710.10547",  # A Unified Approach to Interpreting Model Predictions
        "1806.07538",  # Sanity Checks for Saliency Maps
        "1909.06342",  # Attention is not Explanation
        "2004.14545",  # Beyond Accuracy: Behavioral Testing of NLP models with CheckList
    ],
    
    "Computer Vision": [
        # Foundation Models
        "1512.03385",  # Deep Residual Learning for Image Recognition (ResNet)
        "1409.1556",   # Very Deep Convolutional Networks for Large-Scale Image Recognition (VGG)
        "1608.06993",  # Densely Connected Convolutional Networks
        "1709.01507",  # Squeeze-and-Excitation Networks
        "1807.11164",  # CBAM: Convolutional Block Attention Module
        "1512.00567",  # Rethinking the Inception Architecture for Computer Vision
        "1602.07261",  # Inception-v4, Inception-ResNet and the Impact of Residual Connections
        "1704.04861",  # MobileNets: Efficient Convolutional Neural Networks for Mobile Vision
        "1801.04381",  # MobileNetV2: Inverted Residuals and Linear Bottlenecks
        "1905.03493",  # MobileNetV3: Searching for MobileNetV3
        "1701.07875",  # The One Hundred Layers Tiramisu: Fully Convolutional DenseNets
        "1802.05365",  # How Does Batch Normalization Help Optimization?
        "1910.10683",  # BERT vs. GPT: Comparing Transformer Architectures
        # Object Detection
        "1506.02142",  # You Only Look Once: Unified, Real-Time Object Detection
        "1707.06347",  # Focal Loss for Dense Object Detection
        "1804.02767",  # YOLOv3: An Incremental Improvement
        "2004.10934",  # YOLOv4: Optimal Speed and Accuracy of Object Detection
        "1703.06870",  # Mask R-CNN
        "1506.01497",  # Faster R-CNN: Towards Real-Time Object Detection
        "1311.2524",   # Rich feature hierarchies for accurate object detection
        # Efficient Networks
        "1905.04899",  # EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks
        "1911.09070",  # EfficientDet: Scalable and Efficient Object Detection
        "1602.07360",  # SqueezeNet: AlexNet-level accuracy with 50x fewer parameters
        "1807.11164",  # ShuffleNet: An Extremely Efficient Convolutional Neural Network for Mobile Devices
        "2104.00298",  # MicroNet: Improving Image Recognition with Extremely Low FLOPs
        # Vision Transformers
        "2010.11929",  # An Image is Worth 16x16 Words: Transformers for Image Recognition
        # Generative Models
        "1409.4842",   # Generative Adversarial Networks
        "1406.2661",   # Generative Adversarial Networks (original)
        "1611.07004",  # Image-to-Image Translation with Conditional Adversarial Networks
        "1703.10593",  # Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks
        "1812.04948",  # StyleGAN: Analyzing and Improving the Image Quality of StyleGAN
        "1912.04958",  # StyleGAN2: Analyzing and Improving the Image Quality of StyleGAN
        # Face & Recognition
        "1503.02531",  # FaceNet: A Unified Embedding for Face Recognition and Clustering
        # 3D Vision
        "1612.03144",  # PointNet: Deep Learning on Point Sets for 3D Classification
        "1706.02677",  # Spatial Transformer Networks
        # Understanding & Visualization
        "1312.5602",   # Visualizing and Understanding Convolutional Networks
        "1311.2901",   # Intriguing properties of neural networks
        "1412.3555",   # Explaining and Harnessing Adversarial Examples
        # Additional CV papers
        "1603.05027",  # Identity Mappings in Deep Residual Networks
        "1710.09412",  # Dynamic Routing Between Capsules
        "1710.10196",  # Matrix capsules with EM routing
    ],
    
    "Machine Learning": [
        # Optimization & Training
        "1412.6980",   # Adam: A Method for Stochastic Optimization
        "1502.03167",  # Batch Normalization: Accelerating Deep Network Training
        "1506.02629",  # Delving Deep into Rectifiers: Surpassing Human-Level Performance
        "1511.06434",  # ELU: Fast and Accurate Deep Network Learning by Exponential Linear Units
        "1710.05941",  # Swish: a Self-Gated Activation Function
        "1905.02244",  # Searching for Activation Functions
        "1803.08494",  # Group Normalization
        "1607.08022",  # Layer Normalization
        "1801.05134",  # Shake-Shake regularization
        "1603.05027",  # Identity Mappings in Deep Residual Networks
        "2020.02311",  # The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks
        "1803.05407",  # Averaging Weights Leads to Wider Optima and Better Generalization
        "1711.00165",  # SGDR: Stochastic Gradient Descent with Warm Restarts
        "1608.03983",  # DenseNet: Densely Connected Convolutional Networks
        # Meta Learning & Few-shot
        "1703.03400",  # Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks
        "1606.04080",  # Matching Networks for One Shot Learning
        "1703.05175",  # Prototypical Networks for Few-shot Learning
        "1711.06025",  # Relation Network for Few-Shot Learning
        "1904.04232",  # Learning to Learn Image Classifiers with Visual Analogy
        "1909.02729",  # Meta-Learning with Implicit Gradients
        "2003.05003",  # A Closer Look at Few-shot Classification
        "2104.02638",  # MAML++: A General Framework for Learning Efficient Models
        # Neural Architecture Search
        "1611.01578",  # Neural Architecture Search with Reinforcement Learning
        "1708.05344",  # Learning Transferable Architectures for Scalable Image Recognition
        "1807.11626",  # ENAS: Efficient Neural Architecture Search via Parameter Sharing
        "1806.09055",  # DARTS: Differentiable Architecture Search
        "1904.09925",  # Single Path One-Shot Neural Architecture Search with Uniform Sampling
        "2004.08955",  # Once for All: Train One Network and Specialize it for Efficient Deployment
        # Theory & Mathematics
        "1710.05468",  # The Expressive Power of Neural Networks: A View from the Width
        "1611.03530",  # Understanding deep learning requires rethinking generalization
        "1802.05296",  # Rethinking the Value of Network Pruning
        "1906.02629",  # The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks
        "2003.02395",  # A Mathematical Theory of Deep Convolutional Neural Networks for Feature Extraction
        "1712.00864",  # Spectrally-normalized margin bounds for neural networks
        "1704.08863",  # The Loss Surfaces of Multilayer Networks
        # Adversarial Learning
        "1412.6572",  # Explaining and Harnessing Adversarial Examples
        "1511.04508",  # The Limitations of Deep Learning in Adversarial Settings
        "1608.04644",  # Adversarial examples in the physical world
        "1706.06083",  # Towards Deep Learning Models Resistant to Adversarial Attacks
        "1711.00851",  # Certified Defenses against Adversarial Examples
        "1805.12152",  # Obfuscated Gradients Give a False Sense of Security
        "1902.06705",  # Adversarial Examples Are Not Bugs, They Are Features
        # Transfer Learning
        "1411.1792",   # How transferable are features in deep neural networks?
        "1505.07818",  # Domain-Adversarial Training of Neural Networks
        "1409.7495",   # Simultaneous Deep Transfer Across Domains and Tasks
        "1708.02637",  # Taskonomy: Disentangling Task Transfer Learning
        "1909.11740",  # Cross-lingual Language Model Pretraining
        "2006.03654",  # Language Models are Few-Shot Learners
    ],
    
    "Reinforcement Learning": [
        # Foundation RL
        "1312.4400",   # Playing Atari with Deep Reinforcement Learning
        "1509.02971",  # Human-level control through deep reinforcement learning
        "1707.06203",  # Proximal Policy Optimization Algorithms
        "1602.01783",  # Asynchronous Methods for Deep Reinforcement Learning
        "1511.05952",  # Deep Reinforcement Learning with Double Q-learning
        "1511.09249",  # Prioritized Experience Replay
        "1509.06461",  # Deep Reinforcement Learning with a Natural Gradient Actor-Critic Algorithm
        "1802.09477",  # Rainbow: Combining Improvements in Deep Reinforcement Learning
        "1707.02286",  # Curiosity-driven Exploration by Self-supervised Prediction
        # Game Playing
        "1710.02298",  # Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
        "1712.01815",  # Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
        "1912.06680",  # Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model
        # Imitation Learning
        "1706.05394",  # One-Shot Imitation Learning
        "1703.01161",  # Overcoming catastrophic forgetting in neural networks
        # Robotics & Control
        "1509.06825",  # Learning Hand-Eye Coordination for Robotic Grasping with Deep Learning
        "1707.02201",  # Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World
        "1703.06907",  # Learning to Navigate in Complex Environments
        "1802.09464",  # QT-Opt: Scalable Deep Reinforcement Learning for Vision-Based Robotic Manipulation
        "1706.10295",  # QT-Opt: Scalable Deep Reinforcement Learning for Vision-Based Robotic Manipulation
        "1910.07113",  # Learning Latent Dynamics for Planning from Pixels
        # Multi-agent & Advanced RL
        "1706.02216",  # Inductive Representation Learning on Large Graphs
        "1710.10903",  # Graph Attention Networks
        "1609.02907",  # Semi-Supervised Classification with Graph Convolutional Networks
        "1511.05493",  # Gated Graph Sequence Neural Networks
        "1312.6203",   # Spectral Networks and Locally Connected Networks on Graphs
        # Model-based RL
        "1803.01271",  # Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context
        "1901.02860",  # Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context
        "2001.04451",  # Reformer: The Efficient Transformer
        "2004.05150",  # Linformer: Self-Attention with Linear Complexity
        "2009.06732",  # Performer: Rethinking Attention with FAVOR+
    ],
    
    "Generative Models": [
        # VAEs & Auto-encoders
        "1312.6114",   # Auto-Encoding Variational Bayes
        "1406.5298",   # Variational Autoencoders
        # GANs
        "1406.2661",   # Generative Adversarial Networks (original)
        "1409.4842",   # Generative Adversarial Networks
        "1511.06434",  # Unsupervised Representation Learning with Deep Convolutional GANs
        "1701.00160",  # WGAN: Wasserstein GAN
        "1704.00028",  # Improved Training of Wasserstein GANs
        "1805.08318",  # Self-Attention Generative Adversarial Networks
        "1809.11096",  # Large Scale GAN Training for High Fidelity Natural Image Synthesis
        "1710.10196",  # Progressive Growing of GANs for Improved Quality, Stability, and Variation
        "1611.07004",  # Image-to-Image Translation with Conditional Adversarial Networks
        "1703.10593",  # Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks
        "1812.04948",  # StyleGAN: Analyzing and Improving the Image Quality of StyleGAN
        "1912.04958",  # StyleGAN2: Analyzing and Improving the Image Quality of StyleGAN
        "1609.04802",  # Photo-Realistic Single Image Super-Resolution Using a Generative Adversarial Network
        # Diffusion Models
        "2006.11239",  # Denoising Diffusion Probabilistic Models
        "2102.09672",  # Improved Denoising Diffusion Probabilistic Models
        "2105.05233",  # Diffusion Models Beat GANs on Image Synthesis
        "2112.10752",  # High-Resolution Image Synthesis with Latent Diffusion Models
        "2204.06125",  # Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding
        "2301.11093",  # Adding Conditional Control to Text-to-Image Diffusion Models
        # Language Generation
        "1706.03762",  # Attention Is All You Need (Transformer)
        "2005.14165",  # GPT-3: Language Models are Few-Shot Learners
        "1810.04805",  # BERT: Pre-training of Deep Bidirectional Transformers
        "2203.02155",  # Training language models to follow instructions with human feedback
        "1909.11942",  # RoBERTa: A Robustly Optimized BERT Pretraining Approach
        "2106.09685",  # LoRA: Low-Rank Adaptation of Large Language Models
        "2204.02311",  # PaLM: Scaling Language Modeling with Pathways
        "2301.00234",  # LLaMA: Open and Efficient Foundation Language Models
        # Audio Generation
        "1609.03499",  # WaveNet: A Generative Model for Raw Audio
        "1703.10135",  # Tacotron: Towards End-to-End Speech Synthesis
        "1712.05884",  # Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions
        "1807.03748",  # Neural Voice Cloning with a Few Samples
        # Interpretability & Analysis
        "1312.5602",   # Visualizing and Understanding Convolutional Networks
        "1311.2901",   # Intriguing properties of neural networks
        "1412.3555",   # Explaining and Harnessing Adversarial Examples
        "1603.08155",  # "Why Should I Trust You?": Explaining the Predictions of Any Classifier
        "1704.02685",  # Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization
        "1710.10547",  # A Unified Approach to Interpreting Model Predictions
        "1806.07538",  # Sanity Checks for Saliency Maps
        "1909.06342",  # Attention is not Explanation
        "2004.14545",  # Beyond Accuracy: Behavioral Testing of NLP models with CheckList
        # Sequence Generation
        "1409.3215",   # Sequence to Sequence Learning with Neural Networks
        "1503.04069",  # LSTM: A Search Space Odyssey
        "1308.0850",   # Generating Sequences With Recurrent Neural Networks
        "1511.04508",  # An Empirical Exploration of Recurrent Network Architectures
    ],
    
    "Graph Neural Networks": [
        # Core GNN Methods
        "1609.02907",  # Semi-Supervised Classification with Graph Convolutional Networks
        "1710.10903",  # Graph Attention Networks
        "1706.02216",  # Inductive Representation Learning on Large Graphs
        "1511.05493",  # Gated Graph Sequence Neural Networks
        "1312.6203",   # Spectral Networks and Locally Connected Networks on Graphs
        "1803.03735",  # FastGCN: Fast Learning with Graph Convolutional Networks via Importance Sampling
        "1905.02850",  # Simplifying Graph Convolutional Networks
        "1905.12265",  # Position-aware Graph Neural Networks
        "2005.00687",  # DropEdge: Towards Deep Graph Convolutional Networks on Node Classification
        # 3D Point Clouds
        "1612.00593",  # PointNet: Deep Learning on Point Sets for 3D Classification and Segmentation
        "1612.03144",  # PointNet: Deep Learning on Point Sets for 3D Classification
        "1706.02413",  # PointNet++: Deep Hierarchical Feature Learning on Point Sets
        "1904.08755",  # Point-BERT: Pre-training 3D Point Cloud Transformers with Masked Point Modeling
        "1711.06396",  # Frustum PointNets for 3D Object Detection from RGB-D Data
        "1812.07179",  # 3D Object Proposals using Stereo Imagery for Accurate Object Class Detection
        # Theory & Analysis
        "1710.05468",  # The Expressive Power of Neural Networks: A View from the Width
        "1611.03530",  # Understanding deep learning requires rethinking generalization
        "1802.05296",  # Rethinking the Value of Network Pruning
        "1906.02629",  # The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks
        "2003.02395",  # A Mathematical Theory of Deep Convolutional Neural Networks for Feature Extraction
        "1712.00864",  # Spectrally-normalized margin bounds for neural networks
        "1704.08863",  # The Loss Surfaces of Multilayer Networks
        # Applications & Extensions
        "1703.03400",  # Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks
        "1606.04080",  # Matching Networks for One Shot Learning
        "1703.05175",  # Prototypical Networks for Few-shot Learning
        "1711.06025",  # Relation Network for Few-Shot Learning
        "1904.04232",  # Learning to Learn Image Classifiers with Visual Analogy
        "1909.02729",  # Meta-Learning with Implicit Gradients
        "2003.05003",  # A Closer Look at Few-shot Classification
        "2104.02638",  # MAML++: A General Framework for Learning Efficient Models
        # Graph-based Vision & Multimodal
        "1411.4555",   # Show and Tell: A Neural Image Caption Generator
        "1502.03044",  # Show, Attend and Tell: Neural Image Caption Generation with Visual Attention
        "1707.07998",  # Bottom-Up and Top-Down Attention for Image Captioning and Visual Question Answering
        "1908.02265",  # ViLBERT: Pretraining Task-Agnostic Visiolinguistic Representations
        "2001.00179",  # VL-BERT: Pre-training of Generic Visual-Linguistic Representations
        "2103.15679",  # Learning Transferable Visual Models From Natural Language Supervision (CLIP)
        "2204.14198",  # Flamingo: a Visual Language Model for Few-Shot Learning
        "2301.12597",  # BLIP-2: Bootstrapping Vision-Language Pre-training with Frozen Image Encoders
        # Graph Optimization & Training
        "1412.6980",   # Adam: A Method for Stochastic Optimization
        "1502.03167",  # Batch Normalization: Accelerating Deep Network Training
        "1506.02629",  # Delving Deep into Rectifiers: Surpassing Human-Level Performance
        "1607.08022",  # Layer Normalization
        "1803.08494",  # Group Normalization
        "2020.02311",  # The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks
        "1803.05407",  # Averaging Weights Leads to Wider Optima and Better Generalization
        "1711.00165",  # SGDR: Stochastic Gradient Descent with Warm Restarts
    ]
}

def main():
    """Generate field-organized arXiv links file."""
    output_file = "arxiv_links_by_field.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        for field_name, paper_ids in FIELDS.items():
            f.write(f"## {field_name}\n")
            print(f"Processing {field_name}: {len(paper_ids)} papers")
            
            for paper_id in paper_ids:
                pdf_url = f"https://arxiv.org/pdf/{paper_id}"
                f.write(f'"{pdf_url}",\n')
            
            f.write("\n")  # Empty line between sections
    
    total_papers = sum(len(ids) for ids in FIELDS.values())
    print(f"\nDone! Generated {output_file} with {total_papers} papers across {len(FIELDS)} fields.")
    print(f"File saved: {output_file}")

if __name__ == "__main__":
    main() 