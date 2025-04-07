# Define all stored procedures as SQL strings
STORED_PROCEDURES = {
    # Authentication procedures
    "auth_login": """
    -- DROP FUNCTION public.auth_login(text);
    CREATE OR REPLACE FUNCTION public.auth_login(p_email text)
    RETURNS TABLE(id uuid, email character varying, name character varying, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $function$
        BEGIN
            RETURN QUERY
            SELECT 
                u.id::UUID,
                u.email,
                u.name,
                u.created_at
            FROM 
                users u
            WHERE 
                u.email = p_email;
        END;
        $function$
    ;

    """,
    
    "auth_verify_user": """
    -- DROP FUNCTION public.auth_verify_user(text);

    CREATE OR REPLACE FUNCTION public.auth_verify_user(p_user_id text)
    RETURNS TABLE(id character varying, email character varying, name character varying, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $function$
        BEGIN
            RETURN QUERY
            SELECT
                u.id,
                u.email,
                u.name,
                u.created_at
            FROM
                users u
            WHERE
                u.id = p_user_id::VARCHAR;
        END;
        $function$
    ;

    """,
    
    # User management procedures
    "create_user": """
    -- DROP FUNCTION public.create_user(text, text);
    CREATE OR REPLACE FUNCTION public.create_user(p_email text, p_name text)
    RETURNS TABLE(id character varying, email character varying, name character varying, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        v_user_id UUID;
        inserted_row users%ROWTYPE;
    BEGIN
        -- Insert the new user and get the whole row
        INSERT INTO users (email, name)
        VALUES (p_email, p_name)
        RETURNING * INTO inserted_row;
        
        -- Get the ID from the inserted row
        v_user_id := inserted_row.id;

        -- Return the user info
        RETURN QUERY
        SELECT
            u.id,
            u.email,
            u.name,
            u.created_at
        FROM
            users u
        WHERE
            u.id = v_user_id::VARCHAR;
    END;
    $function$
    ;

    """,
    
    "get_all_users": """
    -- DROP FUNCTION public.get_all_users();
    CREATE OR REPLACE FUNCTION public.get_all_users()
    RETURNS TABLE(id character varying, email character varying, name character varying, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $function$
        BEGIN
            RETURN QUERY
            SELECT 
                u.id,
                u.email,
                u.name,
                u.created_at
            FROM 
                users u
            ORDER BY 
                u.created_at DESC;
        END;
        $function$
    ;
    """,
    "get_user_by_id": """
    -- DROP FUNCTION public.get_user_by_id(uuid);

    CREATE OR REPLACE FUNCTION public.get_user_by_id(p_user_id uuid)
    RETURNS TABLE(id character varying, email character varying, name character varying, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        user_record RECORD;
    BEGIN
        SELECT 
            u.id,
            u.email,
            u.name,
            u.created_at
        INTO user_record
        FROM users u
        WHERE u.id = p_user_id::VARCHAR;

        RETURN QUERY SELECT
            user_record.id,
            user_record.email,
            user_record.name,
            user_record.created_at;
    END;
    $function$
    ;
    """,
    
    # Order management procedures
    "create_order": """
    -- DROP FUNCTION public.create_order(varchar, varchar);

    CREATE OR REPLACE FUNCTION public.create_order(p_user_id uuid, p_customer_name character varying)
    RETURNS uuid
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        new_order_id UUID;
    BEGIN
        -- Generate a new UUID for the order
        new_order_id := gen_random_uuid();

        -- Insert with proper UUID types
        INSERT INTO orders (id, user_id, customer_name, total_price)
        VALUES (
            new_order_id,
            p_user_id,
            p_customer_name,
            0
        )
        RETURNING id INTO new_order_id;

        RETURN new_order_id;
    END;
    $function$
    ;

    """,
    
    "create_or_get_product": """
    -- DROP FUNCTION public.create_or_get_product(varchar, numeric)
    CREATE OR REPLACE FUNCTION public.create_or_get_product(p_name character varying, p_price numeric)
    RETURNS TABLE(id uuid, name character varying, price numeric)
    LANGUAGE plpgsql
    AS $function$
        DECLARE
            product_id UUID;
            product_rec RECORD;
        BEGIN
            -- Check if product exists
            SELECT p.id, p.name, p.price INTO product_rec
            FROM products p
            WHERE p.name = p_name
            LIMIT 1;
            
            -- If product exists, return it
            IF FOUND THEN
                id := product_rec.id;
                name := product_rec.name;
                price := product_rec.price;
                RETURN NEXT;
                RETURN;
            END IF;
            
            -- If product doesn't exist, create a new one
            product_id := gen_random_uuid(); -- Or uuid_generate_v4() depending on your PostgreSQL version
            
            INSERT INTO products (id, name, price, created_at)
            VALUES (product_id, p_name, p_price, CURRENT_TIMESTAMP)
            RETURNING products.id, products.name, products.price INTO product_rec;
            
            id := product_rec.id;
            name := product_rec.name;
            price := product_rec.price;
            RETURN NEXT;
        END;
        $function$
    ;
    """,
    
    "add_product_to_order": """
    -- DROP FUNCTION public.add_product_to_order(uuid, uuid, int4, numeric);
    CREATE OR REPLACE FUNCTION public.add_product_to_order(p_order_id uuid, p_product_id uuid, p_quantity integer, p_unit_price numeric)
    RETURNS uuid
    LANGUAGE plpgsql
    AS $function$
        DECLARE
            new_order_product_id UUID;
        BEGIN
            -- Generate a new UUID for the order product relationship
            new_order_product_id := gen_random_uuid();
            
            -- Cast UUIDs to VARCHAR for insertion
            INSERT INTO order_products (id, order_id, product_id, quantity, unit_price, created_at)
            VALUES (
                new_order_product_id::TEXT, 
                p_order_id::TEXT, 
                p_product_id::TEXT, 
                p_quantity, 
                p_unit_price,
                CURRENT_TIMESTAMP
            )
            RETURNING id::UUID INTO new_order_product_id;
            
            RETURN new_order_product_id;
        END;
        $function$
    ;

    """,
    
    "update_order_total": """
    CREATE OR REPLACE FUNCTION public.update_order_total(p_order_id UUID)
    RETURNS NUMERIC
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        total NUMERIC;
    BEGIN
        -- Cast UUID to VARCHAR for the first comparison
        SELECT COALESCE(SUM(quantity * unit_price), 0)
        INTO total
        FROM order_products
        WHERE order_id = p_order_id::VARCHAR;
        
        -- Cast UUID to VARCHAR for the second comparison
        UPDATE orders
        SET total_price = total
        WHERE id = p_order_id::VARCHAR;
        
        RETURN total;
    END;
    $function$;
    """,
    
    "get_order_details": """
    -- DROP FUNCTION public.get_order_details(uuid);

    CREATE OR REPLACE FUNCTION public.get_order_details(p_order_id uuid)
    RETURNS TABLE(id uuid, user_id uuid, customer_name character varying, total_price numeric, created_at timestamp without time zone, product_id uuid, product_name character varying, quantity integer, unit_price numeric)
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        RETURN QUERY
        SELECT 
            o.id::UUID,
            o.user_id::UUID,
            o.customer_name,
            o.total_price::NUMERIC,
            o.created_at,
            p.id::UUID AS product_id,
            p.name AS product_name,
            op.quantity,
            op.unit_price::NUMERIC
        FROM 
            orders o
        JOIN 
            order_products op ON o.id = op.order_id
        JOIN 
            products p ON op.product_id = p.id
        WHERE 
            o.id = p_order_id::VARCHAR;  -- Add this type cast
    END;
    $function$
    ;

    """,
    
    "get_order_byId": """
    -- DROP FUNCTION public.get_order_byid(uuid, uuid);

    CREATE OR REPLACE FUNCTION public.get_order_byid(p_order_id uuid, p_user_id uuid)
    RETURNS TABLE(id character varying, user_id character varying, customer_name character varying, total_price numeric, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $function$
        BEGIN
            RETURN QUERY
            SELECT
                o.id::VARCHAR(36),
                o.user_id::VARCHAR(36),
                o.customer_name::VARCHAR(50),
                o.total_price::NUMERIC(10,2),
                o.created_at
            FROM
                orders o
            WHERE
                o.id = p_order_id::VARCHAR
                AND o.user_id = p_user_id::VARCHAR;
        END;
        $function$
    ;

    """,
    
    "get_user_orders": """
    -- DROP FUNCTION public.get_user_orders(uuid, varchar, timestamp, timestamp);

    CREATE OR REPLACE FUNCTION public.get_user_orders(p_user_id uuid, p_customer_name character varying DEFAULT NULL::character varying, p_start_date timestamp without time zone DEFAULT NULL::timestamp without time zone, p_end_date timestamp without time zone DEFAULT NULL::timestamp without time zone)
    RETURNS TABLE(id character varying, user_id character varying, customer_name character varying, total_price numeric, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        -- Return orders without pagination
        RETURN QUERY
        SELECT
            o.id::VARCHAR(36),
            o.user_id::VARCHAR(36),
            o.customer_name::VARCHAR(50),
            o.total_price::NUMERIC(10,2),
            o.created_at
        FROM
            orders o
        WHERE
            o.user_id = p_user_id::VARCHAR
            AND (p_customer_name IS NULL OR o.customer_name ILIKE '%' || p_customer_name || '%')
            AND (p_start_date IS NULL OR o.created_at >= p_start_date)
            AND (p_end_date IS NULL OR o.created_at <= p_end_date)
        ORDER BY
            o.created_at DESC;
    END;
    $function$
    ;

    """,
    
    "get_order_products_by_ids": """
    -- DROP FUNCTION public.get_order_products_by_ids(text);
    CREATE OR REPLACE FUNCTION public.get_order_products_by_ids(p_order_ids text)
    RETURNS TABLE(order_id character varying, product_id character varying, product_name character varying, quantity integer, unit_price numeric)
    LANGUAGE plpgsql
    AS $function$
        BEGIN
            RETURN QUERY
            SELECT
                op.order_id,
                p.id AS product_id,
                p.name AS product_name,
                op.quantity,
                op.unit_price::NUMERIC(10,2)
            FROM
                order_products op
            JOIN
                products p ON op.product_id = p.id
            WHERE
                op.order_id IN (
                    SELECT unnest(string_to_array(p_order_ids, ','))
                )
            ORDER BY
                op.order_id, p.name;
        END;
        $function$
    ;

    """,
    
    # Reporting procedures
    "get_product_sales_report": """
    -- DROP FUNCTION public.get_product_sales_report(text, timestamp, timestamp);

    CREATE OR REPLACE FUNCTION public.get_product_sales_report(p_user_id text, p_start_date timestamp without time zone, p_end_date timestamp without time zone)
    RETURNS TABLE(product_name character varying, total_quantity bigint, total_price double precision)
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        RETURN QUERY
        SELECT 
            p.name AS product_name,
            SUM(op.quantity)::BIGINT AS total_quantity,
            SUM(op.quantity * op.unit_price)::FLOAT AS total_price
        FROM 
            products p
        JOIN 
            order_products op ON p.id = op.product_id
        JOIN 
            orders o ON op.order_id = o.id
        WHERE 
            o.user_id = p_user_id
            AND o.created_at >= p_start_date
            AND o.created_at <= p_end_date
        GROUP BY 
            p.name
        ORDER BY 
            total_quantity DESC;
    END;
    $function$
    ;

    """
}