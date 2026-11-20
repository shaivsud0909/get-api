from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product, ProductDetails
from app.database.models import ProductImage as ProductImageModel
from app.products.schema import ProductFeatures
from app.products.schema import ProductImage as ProductImageSchema


async def add_feature(product_id: int,data: ProductFeatures,db: AsyncSession):
    try:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )

        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        detail = ProductDetails(
            product_id=product_id,
            key=data.key,
            value=data.value,
            detailed_description=data.detailed_description,
        )

        db.add(detail)

        await db.commit()
        await db.refresh(detail)

        return detail

    except HTTPException:
        raise

    except Exception:
        await db.rollback()
        raise


async def update_feature(product_id: int, feature_id: int, data: ProductFeatures, db: AsyncSession):
    try:
        result = await db.execute(
            select(ProductDetails).where(ProductDetails.id == feature_id, ProductDetails.product_id == product_id)
        )

        feature = result.scalar_one_or_none()

        if not feature:
            raise HTTPException(
                status_code=404,
                detail="Feature not found"
            )

        feature.key = data.key
        feature.value = data.value
        feature.detailed_description = data.detailed_description

        await db.commit()
        await db.refresh(feature)

        return feature

    except HTTPException:
        raise

    except Exception:
        await db.rollback()
        raise

async def delete_feature(product_id: int, feature_id: int, db: AsyncSession):
    try:
        result = await db.execute(
            select(ProductDetails).where(ProductDetails.id == feature_id, ProductDetails.product_id == product_id)
        )

        feature = result.scalar_one_or_none()

        if not feature:
            raise HTTPException(
                status_code=404,
                detail="Feature not found"
            )

        await db.delete(feature)
        await db.commit()

        return {"detail": "Feature deleted successfully"}

    except HTTPException:
        raise

    except Exception:
        await db.rollback()
        raise

async def add_image(product_id: int, data: ProductImageSchema, file: UploadFile, db: AsyncSession):
    try:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )

        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        image = ProductImageModel(
            product_id=product_id,
            image_url=file.filename,
            alt_text=data.alt_text,
            is_primary=data.is_primary,
        )

        db.add(image)

        await db.commit()
        await db.refresh(image)

        return image

    except HTTPException:
        raise

    except Exception:
        await db.rollback()
        raise

async def get_product_features(product_id: int, db: AsyncSession):
    try:
        features_result = await db.execute(
            select(ProductDetails).where(ProductDetails.product_id == product_id)
        )
        images_result = await db.execute(
            select(ProductImageModel).where(ProductImageModel.product_id == product_id)
        )

        features = features_result.scalars().all()
        images = images_result.scalars().all()

        return {
            "features": features,
            "images": [
                {"image_url": image.image_url, "alt_text": image.alt_text}
                for image in images
            ],
        }

    except Exception:
        raise
