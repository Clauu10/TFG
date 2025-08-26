from torchvision import transforms

TRANSFORMS_CONFIG = {
    "plastic": {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(384, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomGrayscale(p=0.2),
            transforms.RandomPerspective(distortion_scale=0.3, p=0.4),
            transforms.RandomAffine(degrees=15, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.RandomErasing(p=0.25),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ]),
        "test": transforms.Compose([
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
    },
    "detergent": {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(384, scale=(0.85, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=12),
            transforms.ColorJitter(
                brightness=0.4,
                contrast=0.4,
                saturation=0.4,
                hue=0.1
            ),
            transforms.RandomAffine(
                degrees=0,
                translate=(0.1, 0.1),
                scale=(0.9, 1.15)
            ),
            transforms.RandomPerspective(
                distortion_scale=0.3,
                p=0.6
            ),
            transforms.ToTensor(),  
            transforms.RandomErasing(p=0.15),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ]),
        "test": transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    },
    "glass": {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(256, scale=(0.9, 1.0)),
            transforms.RandomHorizontalFlip(p=0.3),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ]),
        "test": transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
    },
    "cardboard": {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(384, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(8),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.04),
            transforms.RandomPerspective(distortion_scale=0.15, p=0.3),
            transforms.ToTensor(),
            transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
            transforms.RandomErasing(p=0.2, scale=(0.02,0.08), ratio=(0.3,3.3))
        ]),
        "test": transforms.Compose([
            transforms.Resize(420),
            transforms.CenterCrop(384),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],[0.229, 0.224, 0.225]),
        ])
    },
    "multiclase": {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(256, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                [0.229, 0.224, 0.225]),
            transforms.RandomErasing(p=0.25)
        ]),
        "test": transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
    }
}
